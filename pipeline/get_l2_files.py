import datetime as dt
import glob
import importlib
import math
import pickle
from pathlib import Path

import get_lexi_l1c_data as gl1c
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.wcs import WCS

importlib.reload(gl1c)


# Define a list of global variables
# Define the field of view of LEXI in degrees
LEXI_FOV = 9.1

# roll angle: position angle measured from North (Dec+) through East (RA+), degrees
ROLL_DEG = 157.3949

# Half-widths of the FOV along instrument axes (degrees).
FOV_U = LEXI_FOV * 0.5
FOV_V = LEXI_FOV * 0.5

theta = np.deg2rad(ROLL_DEG)


def vignette(d: float = 0.0):
    """
    Function to calculate the vignetting factor for a given distance from boresight

    Parameters
    ----------
    d : float
        Distance from boresight in degrees

    Returns
    -------
    f : float
        Vignetting factor

    """

    # Set the vignetting factor
    # f = 1.0 - 0.5 * (d / (LEXI_FOV * 0.5)) ** 2
    f = 1

    return f


def rotate_sky_to_instr(dx, dy, theta):
    """
    Rotate sky offsets (x=East, y=North) into instrument (u,v), where the +v axis
    is at position angle 'theta' from North through East.
    For PA from North through East, the transform is:
        u =  x*cos(theta) + y*sin(theta)
        v = -x*sin(theta) + y*cos(theta)
    """
    u = dx * np.cos(theta) + dy * np.sin(theta)
    v = -dx * np.sin(theta) + dy * np.cos(theta)
    return u, v


def small_angle_offsets_deg(ra_grid_deg, dec_grid_deg, ra0_deg, dec0_deg):
    """
    Small-angle tangent-plane offsets in degrees from (ra0, dec0):
      dx = (RA - RA0) * cos(dec0)  [East]
      dy = (Dec - Dec0)            [North]
    Includes RA wrap handling.
    """
    # RA difference with wrap handling to [-180, 180)
    dra = (ra_grid_deg - ra0_deg + 180.0) % 360.0 - 180.0
    # project RA separation by cos(dec0)
    dx = dra * np.cos(np.deg2rad(dec0_deg))
    dy = dec_grid_deg - dec0_deg
    return dx, dy


def vignette_uv(u, v):
    """
    Example elliptical support: inside ellipse => apply your vignette as function of
    elliptical radius; outside => 0.
    For circular, set FOV_U == FOV_V.
    """
    # Elliptical normalized radius
    r_ell = np.sqrt((u / FOV_U) ** 2 + (v / FOV_V) ** 2)
    r_equiv = r_ell * max(FOV_U, FOV_V)

    return np.where(r_ell <= 1.0, vignette(r_equiv), 0.0)


def calc_exposure_maps(
    time_range: list = None,
    time_zone: str = "UTC",
    interp_method: str = "linear",
    time_step: float = 1,
    ra_range: list = [0, 360],
    dec_range: list = [-90, 90],
    ra_res: float = 0.5,
    dec_res: float = 0.5,
    time_integrate: float = None,
    save_exposure_map_file: bool = False,
    save_exposure_map_image: bool = False,
    verbose: bool = True,
    force_compute: bool = False,
    array_to_image_kwargs: dict = {},
):

    spc_df = pd.read_csv(
        "../data/pointing/lexi_look_direction_data_resampled_interpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
    )
    spc_df["RA"] = spc_df["ra_lexi"]
    spc_df["DEC"] = spc_df["dec_lexi"]

    # Set Epoch as index and convert to datetime
    spc_df["Epoch"] = pd.to_datetime(spc_df["Epoch"], utc=True)
    spc_df.set_index("Epoch", inplace=True)

    # If the elemnts in time range are strings, convert them to datetime
    if time_integrate is not None:
        if isinstance(time_range[0], str) and isinstance(time_range[1], str):
            time_range = [pd.to_datetime(t).tz_localize(time_zone) for t in time_range]
    # Validate time_integrate
    if time_integrate is None:
        # If time_integrate is not provided, set it to the timedelta of the provided time_range
        time_range = [pd.to_datetime(t).tz_localize(time_zone) for t in time_range]
        time_integrate = (time_range[1] - time_range[0]).total_seconds()
        if verbose:
            print(
                f"\033[1;91m Integration time \033[1;92m (time_integrate) \033[1;91m not provided. Setting integration time to the time span of the spacecraft ephemeris data: \033[1;92m {time_integrate} seconds \033[0m\n"
            )

    # Set up coordinate grid
    ra_arr = np.arange(ra_range[0], ra_range[1], ra_res)
    dec_arr = np.arange(dec_range[0], dec_range[1], dec_res)
    ra_grid = np.tile(ra_arr, (len(dec_arr), 1)).transpose()
    dec_grid = np.tile(dec_arr, (len(ra_arr), 1))

    try:
        # If force_compute is set to True, then go to the except block
        if force_compute:
            raise FileNotFoundError
        # Read the exposure map from a pickle file, if it exists
        # Define the folder where the exposure maps are saved
        save_folder = Path.cwd() / "data/exposure_maps"
        t_start = time_range[0].strftime("%Y%m%d_%H%M%S")
        t_stop = time_range[1].strftime("%Y%m%d_%H%M%S")
        ra_start = ra_range[0]
        ra_stop = ra_range[1]
        dec_start = dec_range[0]
        dec_stop = dec_range[1]
        ra_res = ra_res
        dec_res = dec_res
        time_integrate = int(time_integrate)
        exposure_maps_file_name = (
            f"{save_folder}/lexi_exposure_map_Tstart_{t_start}_Tstop_{t_stop}_RAstart_{ra_start}"
            f"_RAstop_{ra_stop}_RAres_{ra_res}_DECstart_{dec_start}_DECstop_{dec_stop}_DECres_"
            f"{dec_res}_Tint_{time_integrate}.npy"
        )
        # Read the exposure map from the pickle file
        exposure_maps_dict = pickle.load(open(exposure_maps_file_name, "rb"))
        if verbose:
            exposure_maps_file_dir = Path(exposure_maps_file_name).parent
            exposure_maps_file_name = Path(exposure_maps_file_name).name
            print(
                f"Exposure map loaded from file \033[1;94m {exposure_maps_file_dir}/\033[1;92m{exposure_maps_file_name} \033[0m\n"
            )
    except FileNotFoundError:
        print("Exposure map not found, computing now. This may take a while \n")

        # Slice to relevant time range; make groups of rows spanning time_integratetion
        spc_df_selected = spc_df.loc[time_range[0] : time_range[1]]

        resampled_groups = spc_df_selected.resample(
            pd.Timedelta(time_integrate, unit="s"), origin="start"
        )
        # Filter out groups that fall outside the time_range
        integ_groups = [
            group
            for _, group in resampled_groups
            if not group.empty
            and group.index.min() >= time_range[0]
            and group.index.max() <= time_range[1]
        ]
        # Filter out the groups if their minimum and maximum times are same
        integ_groups = [group for group in integ_groups if group.index.min() != group.index.max()]
        # Get the min and max times of each group
        start_time_arr = []
        stop_time_arr = []
        for group in integ_groups:
            start_time_arr.append(group.index.min())
            stop_time_arr.append(group.index.max())

        # Make as many empty exposure maps as there are integration groups
        exposure_maps = np.zeros((len(integ_groups), len(ra_arr), len(dec_arr)))

        # Loop through each pointing step and add the exposure to the map
        for map_idx, (group) in enumerate(integ_groups):
            for row in group.itertuples():
                # Pointing (boresight) in degrees
                ra0 = float(row.RA)  # ensure plain float
                dec0 = float(row.DEC)

                # Small-angle offsets (degrees) on the tangent plane
                dx, dy = small_angle_offsets_deg(ra_grid, dec_grid, ra0, dec0)  # x=East, y=North

                # Rotate into instrument frame (u,v) using roll angle
                u, v = rotate_sky_to_instr(dx, dy, theta)

                # Build exposure delta with circular FOV + vignette
                exposure_delt = vignette_uv(u, v) * time_step

                # Accumulate
                exposure_maps[map_idx] += exposure_delt

                if verbose:
                    print(
                        f"Computing exposure map ==> \x1b[1;32;255m {np.round(map_idx/len(integ_groups)*100, 6)}\x1b[0m % complete",
                        end="\r",
                    )

        t_start = time_range[0].strftime("%Y%m%d_%H%M%S")
        t_stop = time_range[1].strftime("%Y%m%d_%H%M%S")
        ra_start = ra_range[0]
        ra_stop = ra_range[1]
        dec_start = dec_range[0]
        dec_stop = dec_range[1]
        ra_res = ra_res
        dec_res = dec_res
        time_integrate = int(time_integrate)

        # Define a dictionary to store the exposure maps, ra_arr, and dec_arr, time_range, and time_integrate,
        # ra_range, and dec_range, ra_res, and dec_res
        exposure_maps_dict = {
            "exposure_maps": exposure_maps,
            "ra_arr": ra_arr,
            "dec_arr": dec_arr,
            "time_range": time_range,
            "time_integrate": time_integrate,
            "ra_range": ra_range,
            "dec_range": dec_range,
            "ra_res": ra_res,
            "dec_res": dec_res,
            "start_time_arr": start_time_arr,
            "stop_time_arr": stop_time_arr,
        }
        if save_exposure_map_file:
            # Define the folder to save the exposure maps to
            save_folder = Path.cwd() / "data/exposure_maps"
            Path(save_folder).mkdir(parents=True, exist_ok=True)

            exposure_maps_file_name = (
                f"{save_folder}/lexi_exposure_map_Tstart_{t_start}_Tstop_{t_stop}_RAstart_{ra_start}"
                f"_RAstop_{ra_stop}_RAres_{ra_res}_DECstart_{dec_start}_DECstop_{dec_stop}_DECres_"
                f"{dec_res}_Tint_{time_integrate}.npy"
            )

            # Save the exposure map array to a pickle file
            with open(exposure_maps_file_name, "wb") as f:
                pickle.dump(exposure_maps_dict, f)
            if verbose:
                exposure_maps_file_dir = Path(exposure_maps_file_name).parent
                exposure_maps_file_name = Path(exposure_maps_file_name).name
                print(
                    f"Exposure map saved to file \033[1;94m {exposure_maps_file_dir}/\033[1;92m{exposure_maps_file_name} \033[0m\n"
                )

    # If requested, save the exposure maps as images
    if save_exposure_map_image:
        if verbose:
            print("Saving exposure maps as images")
        # Check if the following keys are present in the array_to_image_kwargs dictionary, if not
        # then add them:
        # - x_range
        # - y_range
        # - save
        if "x_range" not in array_to_image_kwargs:
            array_to_image_kwargs["x_range"] = ra_range
        elif "x_range" in array_to_image_kwargs:
            # Check to ensure that the x_range is the same as the ra_range
            if array_to_image_kwargs["x_range"] != ra_range:
                array_to_image_kwargs["x_range"] = ra_range
                if verbose:
                    print(
                        f"\033[1;91m x_range \033[1;92m (x_range) \033[1;91m in array_to_image_kwargs is not the same as the RA range. Setting x_range to the RA range: \033[1;92m {ra_range} \033[0m\n"
                    )
        if "y_range" not in array_to_image_kwargs:
            array_to_image_kwargs["y_range"] = dec_range
        elif "y_range" in array_to_image_kwargs:
            # Check to ensure that the y_range is the same as the dec_range
            if array_to_image_kwargs["y_range"] != dec_range:
                array_to_image_kwargs["y_range"] = dec_range
                if verbose:
                    print(
                        f"\033[1;91m y_range \033[1;92m (y_range) \033[1;91m in array_to_image_kwargs is not the same as the DEC range. Setting y_range to the DEC range: \033[1;92m {dec_range} \033[0m\n"
                    )
        if "save" not in array_to_image_kwargs:
            array_to_image_kwargs["save"] = save_exposure_map_image
        for i, exposure in enumerate(exposure_maps_dict["exposure_maps"]):
            print(exposure)
            array_to_image(
                input_array=exposure,
                key="exposure_maps",
                start_time=exposure_maps_dict["start_time_arr"][i],
                stop_time=exposure_maps_dict["stop_time_arr"][i],
                ra_res=ra_res,
                dec_res=dec_res,
                time_integrate=exposure_maps_dict["time_integrate"],
                # figure_title="Exposure Map",
                **(array_to_image_kwargs if array_to_image_kwargs else {}),
            )

    return exposure_maps_dict


def make_background_file(
    start_time: dt.datetime | pd.Timestamp,
    end_time: dt.datetime | pd.Timestamp,
    fits_folder: str = "../data/background_files/fits_files/1min/",
    out_dir: str = "../data/background_files/pickle_files/",
    reducer=np.mean,
    strict_consecutive: bool = False,
):
    """
    Aggregate FITS files in [start_time, end_time] into one background payload and save it as a pickle.

    Features:
      - Selects files by *minute-stamped* filenames (YYYY-MM-DDTHH:MM:SS.fits.gz).
      - Accepts arbitrary timestamps; auto-expands to full minutes (floor start, ceil end).
      - Per-pixel center RA/Dec via spherical centroid of 4 corners (robust to RA wrap).
      - Per-pixel area as spherical quadrilateral (two triangles), in arcmin^2.

    Returns
    -------
    payload : dict
        Dict with keys:
          ra_edges, dec_edges, background, wcs_header_dict, files_used,
          ra_center, dec_center, corner_radec,
          ra_center_map, dec_center_map, ra_dec_area
    """
    fits_files = sorted(glob.glob(str(Path(fits_folder) / "*.fits.gz")))

    # -----------------
    # Helpers
    # -----------------
    def load_data_and_wcs(fp):
        with fits.open(fp) as hdul:
            hdu = hdul[0]
            data = np.asarray(hdu.data, dtype=float)
            hdr = hdu.header
        return data, hdr, WCS(hdr)

    def wcs_header_to_dict(w):
        h = w.to_header(relax=True)
        return {k: (h[k], h.comments[k]) for k in h.keys()}

    def strip_fits_suffix(p: Path) -> str:
        # handles .fits and .fits.gz
        return Path(p.stem).stem

    def parse_timestamp_from_name(name: str) -> dt.datetime:
        # filenames are UTC, exact second
        return dt.datetime.strptime(name, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)

    def format_timestamp(obj) -> str:
        if isinstance(obj, str):
            d = parse_timestamp_from_name(obj)
        elif isinstance(obj, pd.Timestamp):
            d = obj.to_pydatetime()
        elif isinstance(obj, dt.datetime):
            d = obj
        else:
            raise TypeError("format_timestamp expects str | datetime | pandas.Timestamp")
        return d.strftime("%Y%m%d_%H%M%S")

    def spherical_centroid(ra_deg: np.ndarray, dec_deg: np.ndarray) -> tuple[float, float]:
        ra = np.radians(ra_deg)
        dec = np.radians(dec_deg)
        x = np.cos(dec) * np.cos(ra)
        y = np.cos(dec) * np.sin(ra)
        z = np.sin(dec)
        x_m, y_m, z_m = x.mean(), y.mean(), z.mean()
        r_xy = math.hypot(x_m, y_m)
        ra_c = (math.degrees(math.atan2(y_m, x_m)) + 360.0) % 360.0
        dec_c = math.degrees(math.atan2(z_m, r_xy))
        return ra_c, dec_c

    def spherical_centroid_vec(
        ra_deg4: np.ndarray, dec_deg4: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        ra = np.radians(ra_deg4)
        dec = np.radians(dec_deg4)
        x = np.cos(dec) * np.cos(ra)
        y = np.cos(dec) * np.sin(ra)
        z = np.sin(dec)
        x_m = x.mean(axis=-1)
        y_m = y.mean(axis=-1)
        z_m = z.mean(axis=-1)
        r_xy = np.hypot(x_m, y_m)
        ra_c = (np.degrees(np.arctan2(y_m, x_m)) + 360.0) % 360.0
        dec_c = np.degrees(np.arctan2(z_m, r_xy))
        return ra_c, dec_c

    # --- Spherical geometry for per-pixel area ---
    def _wrap_dlon(lon2, lon1):
        d = lon2 - lon1
        return (d + np.pi) % (2.0 * np.pi) - np.pi

    def central_angle(lon1, lat1, lon2, lat2):
        dlat = lat2 - lat1
        dlon = _wrap_dlon(lon2, lon1)
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        a = np.clip(a, 0.0, 1.0)
        return 2.0 * np.arcsin(np.sqrt(a))

    def spherical_triangle_area_lhuilier(a, b, c):
        s = 0.5 * (a + b + c)
        t1 = np.tan(s / 2.0)
        t2 = np.tan((s - a) / 2.0)
        t3 = np.tan((s - b) / 2.0)
        t4 = np.tan((s - c) / 2.0)
        prod = np.clip(t1 * t2 * t3 * t4, 0.0, None)
        E_over4 = np.arctan(np.sqrt(prod))
        return 4.0 * E_over4  # steradians

    def spherical_quad_area_sr(lon00, lat00, lon10, lat10, lon01, lat01, lon11, lat11):
        a1 = central_angle(lon10, lat10, lon11, lat11)
        b1 = central_angle(lon11, lat11, lon00, lat00)
        c1 = central_angle(lon00, lat00, lon10, lat10)
        A1 = spherical_triangle_area_lhuilier(a1, b1, c1)

        a2 = central_angle(lon11, lat11, lon01, lat01)
        b2 = central_angle(lon01, lat01, lon00, lat00)
        c2 = central_angle(lon00, lat00, lon11, lat11)
        A2 = spherical_triangle_area_lhuilier(a2, b2, c2)

        return A1 + A2

    SR_TO_ARCMIN2 = (180.0 / np.pi * 60.0) ** 2  # 1 sr in arcmin^2

    # -----------------
    # Normalize input times to full minutes
    # -----------------
    def to_datetime_aware(x):
        if isinstance(x, pd.Timestamp):
            return x.to_pydatetime()
        return x

    start_time = to_datetime_aware(start_time)
    end_time = to_datetime_aware(end_time)

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=dt.timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=dt.timezone.utc)

    def floor_to_minute(t: dt.datetime) -> dt.datetime:
        return t.replace(second=0, microsecond=0)

    def ceil_to_minute(t: dt.datetime) -> dt.datetime:
        if t.second == 0 and t.microsecond == 0:
            return t
        return (t + dt.timedelta(minutes=1)).replace(second=0, microsecond=0)

    start_time_floor = floor_to_minute(start_time)
    end_time_ceil = ceil_to_minute(end_time)

    # -----------------
    # Select files in [start_time_floor, end_time_ceil]
    # -----------------
    time_indexed = []
    for fp in fits_files:
        stem = strip_fits_suffix(Path(fp))
        try:
            ts = parse_timestamp_from_name(stem)  # tz-aware UTC
        except ValueError:
            continue
        if start_time_floor <= ts <= end_time_ceil:
            time_indexed.append((ts, fp))

    time_indexed.sort(key=lambda t: t[0])

    if not time_indexed:
        raise FileNotFoundError(
            f"No FITS files found between {start_time} and {end_time} in {fits_folder}"
        )

    if strict_consecutive:
        expected = time_indexed[0][0]
        for ts, _ in time_indexed[1:]:
            if ts - expected != dt.timedelta(minutes=1):
                raise ValueError(
                    f"Gap detected. Expected {expected + dt.timedelta(minutes=1)} but found {ts}"
                )
            expected = ts

    # -----------------
    # Load, validate, stack, reduce
    # -----------------
    ref_data, ref_hdr, ref_w = load_data_and_wcs(time_indexed[0][1])
    ny, nx = ref_data.shape
    stack = [ref_data]
    for ts, fp in time_indexed[1:]:
        d, hdr, w = load_data_and_wcs(fp)
        if d.shape != (ny, nx):
            raise ValueError(f"Shape mismatch in {fp}: {d.shape} vs {(ny, nx)}")
        for key in ("NAXIS1", "NAXIS2", "CTYPE1", "CTYPE2"):
            if hdr.get(key) != ref_hdr.get(key):
                raise ValueError(f"WCS mismatch in {fp}: {key} differs")
        stack.append(d)

    stack = np.stack(stack, axis=0)
    agg = reducer(stack, axis=0).astype(np.float32)

    # -----------------
    # RA/Dec edges, per-pixel centers, per-pixel area
    # -----------------
    y_edges, x_edges = np.mgrid[0 : ny + 1, 0 : nx + 1]
    ra_edges, dec_edges = ref_w.all_pix2world(x_edges, y_edges, 0)  # degrees

    # Per-pixel corners
    ra00 = ra_edges[:-1, :-1]
    ra10 = ra_edges[:-1, 1:]
    ra01 = ra_edges[1:, :-1]
    ra11 = ra_edges[1:, 1:]

    dec00 = dec_edges[:-1, :-1]
    dec10 = dec_edges[:-1, 1:]
    dec01 = dec_edges[1:, :-1]
    dec11 = dec_edges[1:, 1:]

    # Centers via spherical centroid
    ra_corners_px = np.stack([ra00, ra10, ra01, ra11], axis=-1)
    dec_corners_px = np.stack([dec00, dec10, dec01, dec11], axis=-1)
    ra_center_map, dec_center_map = spherical_centroid_vec(ra_corners_px, dec_corners_px)

    # Area via spherical quad (two triangles), in arcmin^2
    lon00 = np.radians(ra00 % 360.0)
    lon10 = np.radians(ra10 % 360.0)
    lon01 = np.radians(ra01 % 360.0)
    lon11 = np.radians(ra11 % 360.0)

    lat00 = np.radians(dec00)
    lat10 = np.radians(dec10)
    lat01 = np.radians(dec01)
    lat11 = np.radians(dec11)

    area_sr = spherical_quad_area_sr(lon00, lat00, lon10, lat10, lon01, lat01, lon11, lat11)
    ra_dec_area = (area_sr * SR_TO_ARCMIN2).astype(np.float64)

    # Whole-image center from four image-corner pixel centers
    x_c = np.array([0, nx - 1, 0, nx - 1], dtype=float)
    y_c = np.array([0, 0, ny - 1, ny - 1], dtype=float)
    ra_corners_img, dec_corners_img = ref_w.all_pix2world(x_c, y_c, 0)
    ra_center, dec_center = spherical_centroid(ra_corners_img, dec_corners_img)

    # -----------------
    # Serialize payload and write pickle
    # -----------------
    wcs_header_dict = wcs_header_to_dict(ref_w)
    wcs_header_dict["BUNIT"] = ("count/s/arcmin^2", "Units of the background data")

    payload = {
        "ra_edges": ra_edges.astype(np.float64),
        "dec_edges": dec_edges.astype(np.float64),
        "background": agg,
        # "files_used": [fp for _, fp in time_indexed],
        "ra_center": float(ra_center),
        "dec_center": float(dec_center),
        # "corner_radec": np.column_stack([ra_corners_img, dec_corners_img]).astype(np.float64),
        "ra_center_map": ra_center_map.astype(np.float64),
        "dec_center_map": dec_center_map.astype(np.float64),
        "ra_dec_area": ra_dec_area,  # arcmin^2
        "wcs_header_dict": wcs_header_dict,
    }

    actual_start = time_indexed[0][0]
    actual_end = time_indexed[-1][0]
    start_str = format_timestamp(actual_start)
    end_str = format_timestamp(actual_end)

    window_minutes = int((actual_end - actual_start).total_seconds() // 60) + 1
    out_dir = Path(out_dir) / f"{window_minutes}min_by_window"
    out_dir.mkdir(parents=True, exist_ok=True)

    base = f"sky_background_{start_str}_to_{end_str}"
    out_pkl = out_dir / f"{base}.pkl"

    with open(out_pkl, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    return payload


def calc_sky_backgrounds(
    time_range: list = None,
    time_zone: str = "UTC",
    interp_method: str = "linear",
    time_step: float = 1,
    time_integrate: float = None,
    ra_range: list = [0, 360],
    dec_range: list = [-90, 90],
    ra_res: float = 0.5,
    dec_res: float = 0.5,
    save_exposure_map_file: bool = False,
    save_exposure_map_image: bool = False,
    save_sky_backgrounds_file: bool = False,
    save_sky_backgrounds_image: bool = False,
    verbose: bool = True,
    force_compute: bool = False,
    array_to_image_kwargs: dict = {},
):
    """ """

    exposure_map_dict = calc_exposure_maps(
        time_range=time_range,
        time_zone=time_zone,
        interp_method=interp_method,
        time_step=time_step,
        ra_range=ra_range,
        dec_range=dec_range,
        ra_res=ra_res,
        dec_res=dec_res,
        time_integrate=time_integrate,
        save_exposure_map_file=save_exposure_map_file,
        save_exposure_map_image=save_exposure_map_image,
        verbose=verbose,
        array_to_image_kwargs=array_to_image_kwargs,
    )

    # Calculate sky backgrounds
    start_time = exposure_map_dict["start_time_arr"][0]
    stop_time = exposure_map_dict["stop_time_arr"][0]
    start_time_ts = pd.Timestamp(start_time)
    stop_time_ts = pd.Timestamp(stop_time)

    sky_background_payload = make_background_file(
        start_time=start_time_ts,
        end_time=stop_time_ts,
        fits_folder="../data/background_files/fits_files/1min/",
        out_dir="../data/background_files/pickle_files/",
        reducer=np.mean,
        strict_consecutive=False,
    )
    return exposure_map_dict, sky_background_payload


def background_counts_from_exposure(exposure_maps_dict, sky_bgnds_dict):
    """
    Compute counts per background pixel by multiplying:
      background [count/s/arcmin^2] *
      exposure_time_at_pixel_center [s] *
      pixel_area [arcmin^2]

    Assumes exposure maps live on a regular RA/Dec grid given by
    exposure_maps_dict['ra_arr'] (x-axis) and exposure_maps_dict['dec_arr'] (y-axis),
    and that the background grid has per-pixel center coordinates in
    sky_bgnds_dict['ra_center_map'] and ['dec_center_map'].
    """
    # --- Unpack background grid ---
    bg = np.asarray(sky_bgnds_dict["background"])  # (Ny_bg, Nx_bg), count/s/arcmin^2
    ra_c = np.asarray(sky_bgnds_dict["ra_center_map"])  # (Ny_bg, Nx_bg), deg
    dec_c = np.asarray(sky_bgnds_dict["dec_center_map"])  # (Ny_bg, Nx_bg), deg
    area_arcmin2 = np.asarray(sky_bgnds_dict["ra_dec_area"])  # (Ny_bg, Nx_bg), arcmin^2

    # --- Unpack exposure grid ---
    exp_maps = np.asarray(
        exposure_maps_dict["exposure_maps"]
    )  # (Nt, Ny_exp, Nx_exp), seconds per bin per interval
    ra_arr = np.asarray(exposure_maps_dict["ra_arr"])  # (Nx_exp,), deg, increasing
    dec_arr = np.asarray(exposure_maps_dict["dec_arr"])  # (Ny_exp,), deg, increasing

    # Sum exposure over time dimension → total exposure time per RA/Dec bin [s]
    exp_total = exp_maps.sum(axis=0)  # shape is (len(ra_arr), len(dec_arr)) given your allocation

    # map background centers (ra_c, dec_c) to nearest exposure bin
    ra_res = float(np.median(np.diff(ra_arr))) if ra_arr.size > 1 else np.nan
    dec_res = float(np.median(np.diff(dec_arr))) if dec_arr.size > 1 else np.nan
    ra_min, dec_min = float(ra_arr[0]), float(dec_arr[0])

    ra_idx = np.rint((ra_c - ra_min) / ra_res).astype(int)
    dec_idx = np.rint((dec_c - dec_min) / dec_res).astype(int)
    ra_idx = np.clip(ra_idx, 0, ra_arr.size - 1)
    dec_idx = np.clip(dec_idx, 0, dec_arr.size - 1)

    # IMPORTANT: exp_total is [RA, Dec], so index as [ra_idx, dec_idx]
    exp_at_centers = exp_total[ra_idx, dec_idx]

    # Final counts per background pixel
    counts = bg * exp_at_centers * area_arcmin2  # units: counts

    out = {
        "counts_map": counts,  # same shape as background (Ny_bg, Nx_bg)
        "exposure_at_centers_sec": exp_at_centers,
        "background_counts_per_s_per_arcmin2": bg,
        "pixel_area_arcmin2": area_arcmin2,
        "ra_center_map": ra_c,
        "dec_center_map": dec_c,
        "time_range": exposure_maps_dict["time_range"],
        "metadata": {
            "bg_shape": bg.shape,
            "exp_shape": exp_total.shape,
            "ra_range_exposure": (float(ra_arr[0]), float(ra_arr[-1])),
            "dec_range_exposure": (float(dec_arr[0]), float(dec_arr[-1])),
            "ra_dec_step_exposure_deg": (ra_res, dec_res),
            "units": {
                "background": "count/s/arcmin^2",
                "exposure_at_centers": "s",
                "pixel_area": "arcmin^2",
                "counts_map": "count",
            },
        },
    }
    return out


def _centers_to_edges(centers_1d: np.ndarray) -> np.ndarray:
    """
    Convert a 1D array of monotonically increasing or decreasing bin centers
    into bin edges. Handles slight non-uniformity by using midpoints.
    Returns edges in ascending order (as required by np.histogram2d).
    """
    c = np.asarray(centers_1d, dtype=float)
    # Ensure it's 1D
    if c.ndim != 1:
        raise ValueError("centers_1d must be 1D")
    # If decreasing, flip to increasing for edge construction
    flipped = False
    if c[1] < c[0]:
        c = c[::-1]
        flipped = True

    # Internal edges = midpoints
    mids = 0.5 * (c[1:] + c[:-1])
    # Extrapolated first/last edges
    first_edge = c[0] - 0.5 * (c[1] - c[0])
    last_edge = c[-1] + 0.5 * (c[-1] - c[-2])
    edges = np.concatenate([[first_edge], mids, [last_edge]])

    # Return in ascending order (already ensured). Caller can flip hist if needed.
    return edges


def implement_background_correction(
    counts_dict: dict,
):
    """ """
    start = counts_dict["time_range"][0]
    end = counts_dict["time_range"][1]
    # Remove the timezone info for querying the L2 files
    # if start.tzinfo is not None:
    #     start = start.tz_convert("UTC").replace(tzinfo=None)
    # if end.tzinfo is not None:
    #     end = end.tz_convert("UTC").replace(tzinfo=None)
    lexi_df = gl1c.read_all_data_files(
        file_list=None,
        start_time=start,
        end_time=end,
        return_data_type="dataframe",
        kwargs={
            "data_folder_location": "/media/cephadrius/lexi_data/lexi_data/L1c/sci/cdf",
            "version": "latest",
            "start_time": start,
            "end_time": end,
        },
    )

    ra_map = np.asarray(counts_dict["ra_center_map"], dtype=float)
    dec_map = np.asarray(counts_dict["dec_center_map"], dtype=float)
    bg_rate = np.asarray(counts_dict["background_counts_per_s_per_arcmin2"], dtype=float)
    pix_area = np.asarray(counts_dict["pixel_area_arcmin2"], dtype=float)
    expos = np.asarray(counts_dict["exposure_at_centers_sec"], dtype=float)

    H, W = ra_map.shape

    ra_centers_1d = np.nanmedian(ra_map, axis=1)  # length H, increases downwards
    dec_centers_1d = np.nanmedian(dec_map, axis=0)  # length W, increases to the right

    # Convert centers to edges. np.histogram2d requires ASCENDING edges.
    ra_edges = _centers_to_edges(ra_centers_1d)
    dec_edges = _centers_to_edges(dec_centers_1d)

    ra_ev = pd.to_numeric(lexi_df["photon_RA"], errors="coerce").to_numpy(dtype=float)
    dec_ev = pd.to_numeric(lexi_df["photon_Dec"], errors="coerce").to_numpy(dtype=float)

    m = np.isfinite(ra_ev) & np.isfinite(dec_ev)
    ra_ev, dec_ev = ra_ev[m], dec_ev[m]

    if ra_ev.size == 0:
        # Nothing to bin; return zeros and background-only corrected (=> zeros after clip)
        lexi_hist = np.zeros((H, W), dtype=float)
    else:
        # --- Histogram: rows index RA bins, columns index Dec bins ---
        # Note: numpy.histogram2d takes (x, y, bins=[x_edges, y_edges]) and returns H[xbin, ybin]
        H_raw, _, _ = np.histogram2d(ra_ev, dec_ev, bins=[ra_edges, dec_edges])
        # H_raw.shape == (len(ra_edges)-1, len(dec_edges)-1) = (H, W)
        lexi_hist = H_raw.astype(float)

    # --- Expected background counts per pixel = rate (cnt/s/arcmin^2) * area (arcmin^2) * exposure (s) ---
    expected_bg = bg_rate * pix_area * expos

    # --- Background-corrected histogram ---
    lexi_bgnd_corrected = lexi_hist - expected_bg
    # It's common to clip negatives to zero (no physical negative counts after subtraction)
    lexi_bgnd_corrected = np.clip(lexi_bgnd_corrected, 0.0, None)

    # Add results to output dict
    counts_dict["lexi_hist_raw"] = lexi_hist
    counts_dict["expected_bg_counts"] = expected_bg
    counts_dict["lexi_hist_bgnd_corrected"] = lexi_bgnd_corrected
    counts_dict["ra_edges"] = ra_edges
    counts_dict["dec_edges"] = dec_edges

    return counts_dict


def array_to_image(
    input_array: np.ndarray = None,
    key: str = None,
    x_range: list = None,
    y_range: list = None,
    x_lim: list = None,
    y_lim: list = None,
    start_time: pd.Timestamp = None,
    stop_time: pd.Timestamp = None,
    ra_res: float = None,
    dec_res: float = None,
    time_integrate: float = None,
    cmap: str = None,
    cmin: float = None,
    v_min: float = None,
    v_max: float = None,
    norm: mpl.colors.LogNorm = mpl.colors.LogNorm(),
    norm_type: str = "log",
    aspect: str = "equal",
    figure_title: str = None,
    show_colorbar: bool = True,
    cbar_label: str = None,
    cbar_orientation: str = "vertical",
    show_axes: bool = True,
    display: bool = False,
    figure_size: tuple = None,
    figure_format: str = "png",
    figure_font_size: float = 12,
    save: bool = False,
    save_path: str = None,
    save_name: str = None,
    dpi: int = 300,
    dark_mode: bool = False,
    verbose: bool = False,
    display_time: bool = False,
):
    """
    Convert a 2D array to an image.

    Parameters
    ----------
    ra_res : float, optional
        Right ascension resolution in degrees. Default is None.

    dec_res : float, optional
        Declination resolution in degrees. Default is None.

    time_integrate : int or float, optional
        Integration time in seconds. Default is None.

    input_array : np.ndarray
        2D array to convert to an image.

    x_range : list, optional
        Range of the x-axis.  Default is None.

    y_range : list, optional
        Range of the y-axis.  Default is None.

    x_lim : list, optional
        Limits of the x-axis.  Default is None.

    y_lim : list, optional
        Limits of the y-axis.  Default is None.

    v_min : float, optional
        Minimum value of the colorbar.  If None, then the minimum value of the input array is used.
        Default is None.

    v_max : float, optional
        Maximum value of the colorbar.  If None, then the maximum value of the input array is used.
        Default is None.

    cmap : str, optional
        Colormap to use. By default, based on the `key` being plotted it is set to the following:
        - exposure_maps: 'cividis'
        - sky_backgrounds: 'inferno'
        - lexi_images: 'plasma'
        - something else: 'viridis'
        Default is 'viridis'. Other options include 'plasma', 'inferno', 'magma', 'cividis'. See https://matplotlib.org/stable/tutorials/colors/colormaps.html for more options.

    norm : mpl.colors.Normalize, optional
        Normalization to use for the colorbar colors.  Default is None.

    norm_type : str, optional
        Normalization type to use.  Options are 'linear' or 'log'.  Default is 'linear'.

    aspect : str, optional
        Aspect ratio to use.  Default is 'equal'.

    figure_title : str, optional
        Title of the figure.  Default is None.

    show_colorbar : bool, optional
        If True, then show the colorbar.  Default is True.

    cbar_label : str, optional
        Label of the colorbar.  Default is None.

    cbar_orientation : str, optional
        Orientation of the colorbar.  Options are 'vertical' or 'horizontal'.  Default is 'vertical'.

    show_axes : bool, optional
        If True, then show the axes.  Default is True.

    display : bool, optional
        If True, then display the figure.  Default is False.

    figure_size : tuple, optional
        Size of the figure.  Default is None.

    figure_format : str, optional
        Format of the figure.  Default is 'png'.

    figure_font_size : float, optional
        Font size of the figure.  Default is 12.

    save : bool, optional
        If True, then save the figure.  Default is False.

    save_path : str, optional
        Path to save the figure to.  Default is None.

    save_name : str, optional
        Name of the figure to save.  Default is None.

    display_time : bool, optional
        Display the start and end time of the image.  Default is False.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object.
    ax : matplotlib.axes._subplots.AxesSubplot
        Axes object.

    """
    # Try to use latex rendering
    # plt.rc("text", usetex=False)
    # try:
    #     plt.rc("text", usetex=True)
    #     plt.rc("font", family="serif")
    #     plt.rc("font", size=figure_font_size)
    # except Exception:
    #     pass

    # Check whether input_array is a 2D array
    if len(input_array.shape) != 2:
        raise ValueError("input_array must be a 2D array")

    # Mask the input array if cmin is specified
    if cmin is not None:
        input_array = np.ma.masked_less(input_array, cmin)

    # Check whether x_range is a list
    if x_range is not None:
        if not isinstance(x_range, (list, tuple, np.ndarray)):
            raise ValueError("x_range must be a list, tuple, or numpy array")
        if len(x_range) != 2:
            raise ValueError("x_range must be a list of length 2")
    else:
        x_range = x_range

    # Check whether y_range is a list
    if y_range is not None:
        if not isinstance(y_range, (list, tuple, np.ndarray)):
            raise ValueError("y_range must be a list, tuple, or numpy array")
        if len(y_range) != 2:
            raise ValueError("y_range must be a list of length 2")
    else:
        y_range = y_range

    if dark_mode:
        plt.style.use("dark_background")
        facecolor = "k"
        edgecolor = "w"
        textcolor = "w"
    else:
        plt.style.use("default")
        facecolor = "w"
        edgecolor = "k"
        textcolor = "k"

    if v_min is None and v_max is None:
        array_min = np.nanmin(input_array)
        array_max = np.nanmax(input_array)

        if np.isnan(array_min) and np.isnan(array_max):
            array_min = 0.1
            array_max = 1.0
            if verbose:
                print(
                    f"\n\033[91m Warning: Encountered map where array min \033[00m = \033[92m{array_min}\033[00m \033[91m and array max \033[00m = \033[92m{array_max}\033[00m \033[91m are both NaN. Plotting a range of 0.1 to 1.\033[00m \n"
                )
        if array_min == array_max:
            # In theory, could be a real instance of a perfectly flat map;
            # probably, just an integration window with no photons.
            if verbose:
                print(
                    f"\n\033[91m Warning: Encountered map where array min \033[00m = \033[92m{array_min}\033[00m \033[91m and array max \033[00m = \033[92m{array_max}\033[00m \033[91m are both same. Plotting a range of \u00b1 1. \n"
                )
            array_min -= 1
            array_max += 1

        if norm_type == "linear":
            v_min = 0.9 * array_min
            v_max = 1.1 * array_max
            norm = mpl.colors.Normalize(vmin=v_min, vmax=v_max)
        elif norm_type == "log":
            if array_min <= 0:
                v_min = 1e-5
            else:
                v_min = array_min
            if array_max <= 0:
                v_max = 1e-1
            else:
                v_max = array_max
            norm = mpl.colors.LogNorm(vmin=v_min, vmax=v_max)
    elif v_min is not None and v_max is not None:
        if norm_type == "linear":
            norm = mpl.colors.Normalize(vmin=v_min, vmax=v_max)
        elif norm_type == "log":
            if v_min <= 0:
                v_min = 1e-5
            if v_max <= 0:
                v_max = 1e-1
            norm = mpl.colors.LogNorm(vmin=v_min, vmax=v_max)
    else:
        raise ValueError(
            "Either both v_min and v_max must be specified or neither can be specified"
        )

    # Assign "cmap" based on the input "key"
    if cmap is None:
        if "sky_backgrounds" in key:
            cmap = "inferno"
        elif "exposure_maps" in key:
            cmap = "cividis"
        elif "lexi_images" in key:
            cmap = "plasma"
        else:
            cmap = "viridis"
    # Create the figure
    if figure_size is None:
        fig, ax = plt.subplots(dpi=dpi, facecolor=facecolor, edgecolor=edgecolor)
    else:
        fig, ax = plt.subplots(
            figsize=figure_size, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor
        )

    # Plot the image
    im = ax.imshow(
        np.transpose(input_array),
        cmap=cmap,
        norm=norm,
        extent=[
            x_range[0],
            x_range[1],
            y_range[0],
            y_range[1],
        ],
        origin="lower",
        aspect=aspect,
        interpolation=None,
    )

    # Set the x and y limits
    if x_lim is None:
        # Set the x limits to the x_range
        ax.set_xlim(x_range)
    if y_lim is None:
        # Set the y limits to the y_range
        ax.set_ylim(y_range)

    # Turn on the grid
    ax.grid(True, color="k", alpha=0.5, linestyle="-")
    # Turn on minor grid
    ax.minorticks_on()
    # Set the tick label size
    ax.tick_params(labelsize=0.8 * figure_font_size)

    # Add start and stop time as text to the plot
    if display_time:
        ax.text(
            0.05,
            0.93,
            f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            horizontalalignment="left",
            verticalalignment="bottom",
            transform=ax.transAxes,
            fontsize=0.8 * figure_font_size,
            color=textcolor,
        )
        ax.text(
            0.05,
            0.92,
            f"Stop Time: {stop_time.strftime('%Y-%m-%d %H:%M:%S')}",
            horizontalalignment="left",
            verticalalignment="top",
            transform=ax.transAxes,
            fontsize=0.8 * figure_font_size,
            color=textcolor,
        )
    if show_colorbar:
        if cbar_label is None:
            cbar_label = "Counts/sec"
        if cbar_orientation == "vertical":
            cax = fig.add_axes(
                [
                    ax.get_position().x1 + 0.01,
                    ax.get_position().y0,
                    0.02,
                    ax.get_position().height,
                ]
            )
        elif cbar_orientation == "horizontal":
            cax = fig.add_axes(
                [
                    ax.get_position().x0,
                    ax.get_position().y1 + 0.01,
                    ax.get_position().width,
                    0.02,
                ]
            )
        ax.figure.colorbar(
            im,
            cax=cax,
            orientation=cbar_orientation,
            label=cbar_label,
            pad=0.01,
        )
        # Set the colorbar tick label size
        cax.tick_params(labelsize=0.6 * figure_font_size)
        # Set the colorbar label size
        cax.yaxis.label.set_size(0.9 * figure_font_size)

        # If the colorbar is horizontal, then set the location of the colorbar label and the tick
        # labels to be above the colorbar
        if cbar_orientation == "horizontal":
            cax.xaxis.set_ticks_position("top")
            cax.xaxis.set_label_position("top")
            cax.xaxis.tick_top()
        if cbar_orientation == "vertical":
            cax.yaxis.set_ticks_position("right")
            cax.yaxis.set_label_position("right")
            cax.yaxis.tick_right()
    if not show_axes:
        ax.axis("off")
    else:
        ax.set_xlabel("RA [$^\\circ$]", labelpad=0, fontsize=figure_font_size)
        ax.set_ylabel("DEC [$^\\circ$]", labelpad=0, fontsize=figure_font_size)
        ax.set_title(figure_title, fontsize=1.2 * figure_font_size)

    if save:
        if save_path is None:
            save_path = Path.cwd() / f"figures/{key}"
            if verbose:
                print("save_path not provided. Saving figure to default location \n")
        Path(save_path).mkdir(parents=True, exist_ok=True)
        if save_name is None or save_name == "default":
            start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
            stop_time_str = stop_time.strftime("%Y%m%d_%H%M%S")
            save_name = (
                f"{key.split('/')[0]}_Tstart_{start_time_str}_Tstop_{stop_time_str}_RAstart_{x_range[0]}"
                f"_RAstop_{x_range[1]}_RAres_{ra_res}_DECstart_{y_range[0]}_DECstop_{y_range[1]}_DECres_"
                f"{dec_res}_Tint_{time_integrate}"
            )

        save_name = save_name + "." + figure_format
        plt.savefig(
            f"{save_path}/{save_name}",
            format=figure_format,
            dpi=dpi,
            bbox_inches="tight",
        )
        if verbose:
            print(f"Saved figure to ==> \033[1;94m {save_path}/\033[1;92m{save_name} \033[0m \n")

    if display:
        plt.show()
    else:
        plt.close(fig)

    return fig, ax
