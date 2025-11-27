import datetime as dt
import glob
import importlib
import math
import pickle
from pathlib import Path

import convert_radec_to_azel as cradecazel
import get_flat_field_data as gffd
import get_lexi_l1c_data as gl1c
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import save_data_to_cdf_l2_istp as sdtc
import scipy as scipy
import tabulate
from astropy.io import fits
from astropy.wcs import WCS
from spacepy.pycdf import CDF as cdf

importlib.reload(gl1c)
importlib.reload(gffd)
importlib.reload(sdtc)
importlib.reload(cradecazel)


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
    Example elliptical support: inside ellipse => apply vignette as function of
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
    time_step: float = 1,
    ra_range: list = [0, 360],
    dec_range: list = [-90, 90],
    ra_res: float = 0.5,
    dec_res: float = 0.5,
    time_integrate: float = None,
    verbose: bool = True,
    force_compute: bool = False,
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

    # Precompute total rows to track progress correctly across variable-sized groups
    total_rows = sum(len(group) for group in integ_groups)
    processed_rows = 0

    # Loop through each pointing step and add the exposure to the map
    for map_idx, (group) in enumerate(integ_groups):
        group_len = len(group)
        for row_idx, row in enumerate(group.itertuples(), start=1):
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

            processed_rows += 1
            if verbose:
                percent_complete = (processed_rows / total_rows) * 100 if total_rows else 0.0
                print(
                    f"Computing exposure map ==> \x1b[1;32m {np.round(percent_complete, 6)}\x1b[0m % complete",
                    end="\r",
                    flush=True,
                )

    if verbose:
        print(f"Computing exposure map ==> \x1b[1;32m 100.0\x1b[0m % complete")
    # Find the time resolution of the spacecraft ephemeris data
    time_deltas = spc_df_selected.index.to_series().diff().dropna()
    time_res = time_deltas.mode()[0].total_seconds()

    # Multiply the exposure maps by the time resolution of the spacecraft ephemeris data
    exposure_maps *= time_res

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
    Aggregate FITS files over a given time window into a single background
    data product and serialize to a pickle.

    This routine:
      - Selects 1-minute FITS files with UTC timestamps in their names.
      - Floors the start time and ceils the end time to whole minutes.
      - Loads all relevant FITS images and their WCS information.
      - Reduces the stack (mean, median, etc.) pixel-by-pixel.
      - Computes per-pixel RA/Dec edges, spherical centroids, and projected areas.
      - Computes a whole-image pointing center.
      - Stores results and metadata in a dictionary, written as a `.pkl`.

    Parameters
    ----------
    start_time : datetime.datetime or pandas.Timestamp
        Start of aggregation window. Can be timezone-naive (will default to UTC)
        or timezone-aware.
    end_time : datetime.datetime or pandas.Timestamp
        End of aggregation window. Same rules as start_time.
    fits_folder : str, optional
        Path to directory containing 1-minute background FITS files.
        Default is "../data/background_files/fits_files/1min/".
    out_dir : str, optional
        Output directory where pickle files are stored. A subdirectory is created
        for each window length (e.g. "15min_by_window").
    reducer : callable, optional
        Function used to combine the image stack along the time axis.
        Must accept `axis=0`. Examples: np.mean, np.median, np.sum.
    strict_consecutive : bool, optional
        If True, enforce that all selected FITS files form a consecutive
        uninterrupted 1-minute sequence. Raise ValueError if any gap.

    Returns
    -------
    payload : dict
        Dictionary containing:
          - ra_edges (2D array): RA coordinates of pixel edges [deg].
          - dec_edges (2D array): Dec coordinates of pixel edges [deg].
          - background (2D array): Reduced background map.
          - ra_center (float): Image pointing center RA [deg].
          - dec_center (float): Image pointing center Dec [deg].
          - ra_center_map (2D array): Per-pixel RA center [deg].
          - dec_center_map (2D array): Per-pixel Dec center [deg].
          - ra_dec_area (2D array): Per-pixel area [arcmin^2].
          - wcs_header_dict (dict): WCS header keywords and comments.

    Raises
    ------
    FileNotFoundError
        If no FITS files found in the requested interval.
    ValueError
        If FITS shapes or WCS metadata do not match, or if strict_consecutive
        is True and there is a time gap.
    """
    fits_files = sorted(glob.glob(str(Path(fits_folder) / "*.fits.gz")))

    # -----------------
    # Helpers
    # -----------------
    def load_data_and_wcs(fp):
        """
        Open a FITS file and extract image data and WCS.

        Parameters
        ----------
        fp : str or Path
            Path to FITS file.

        Returns
        -------
        data : np.ndarray
            Image array as float.
        hdr : astropy.io.fits.Header
            FITS header.
        w : astropy.wcs.WCS
            WCS object constructed from the header.
        """
        with fits.open(fp) as hdul:
            hdu = hdul[0]
            data = np.asarray(hdu.data, dtype=float)
            hdr = hdu.header
        return data, hdr, WCS(hdr)

    def wcs_header_to_dict(w):
        """
        Convert a WCS object into a dictionary with values and comments.

        Parameters
        ----------
        w : astropy.wcs.WCS
            Input WCS.

        Returns
        -------
        dict
            Mapping of header keyword → (value, comment).
        """
        h = w.to_header(relax=True)
        return {k: (h[k], h.comments[k]) for k in h.keys()}

    def strip_fits_suffix(p: Path) -> str:
        """
        Strip .fits or .fits.gz from filename.

        Parameters
        ----------
        p : Path
            Input path.

        Returns
        -------
        str
            Basename without FITS extensions.
        """
        # handles .fits and .fits.gz
        return Path(p.stem).stem

    def parse_timestamp_from_name(name: str) -> dt.datetime:
        """
        Parse UTC timestamp from FITS filename stem.

        Parameters
        ----------
        name : str
            Expected format: YYYY-MM-DDTHH:MM:SS

        Returns
        -------
        datetime.datetime
            Time with UTC tzinfo.
        """
        # filenames are UTC, exact second
        return dt.datetime.strptime(name, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)

    def format_timestamp(obj) -> str:
        """
        Convert datetime-like to string for filenames.

        Parameters
        ----------
        obj : str | datetime | pandas.Timestamp

        Returns
        -------
        str
            "YYYYMMDD_HHMMSS" string.
        """
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
        """
        Compute spherical centroid of multiple (RA, Dec) points.

        Uses unit-vector averaging to handle wrap-around at RA=0.

        Parameters
        ----------
        ra_deg, dec_deg : array-like
            Arrays of RA, Dec in degrees.

        Returns
        -------
        ra_c, dec_c : float
            Centroid coordinates in degrees.
        """
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
        """
        Vectorized spherical centroid of per-pixel corners.

        Parameters
        ----------
        ra_deg4, dec_deg4 : ndarray
            Shape (..., 4). RA/Dec of four corners of each pixel.

        Returns
        -------
        ra_c, dec_c : ndarray
            Per-pixel centroid RA/Dec [deg].
        """
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
        """
        Wrap longitude difference into [-pi, pi].
        """
        d = lon2 - lon1
        return (d + np.pi) % (2.0 * np.pi) - np.pi

    def central_angle(lon1, lat1, lon2, lat2):
        """
        Great-circle central angle between two points on a sphere.

        Parameters
        ----------
        lon1, lat1, lon2, lat2 : ndarray
            Longitudes and latitudes in radians.

        Returns
        -------
        ndarray
            Central angle in radians.
        """
        dlat = lat2 - lat1
        dlon = _wrap_dlon(lon2, lon1)
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        a = np.clip(a, 0.0, 1.0)
        return 2.0 * np.arcsin(np.sqrt(a))

    def spherical_triangle_area_lhuilier(a, b, c):
        """
        Spherical triangle area (steradians) via L'Huilier's theorem.

        Parameters
        ----------
        a, b, c : float or ndarray
            Side lengths (radians).

        Returns
        -------
        float or ndarray
            Triangle area in steradians.
        """
        s = 0.5 * (a + b + c)
        t1 = np.tan(s / 2.0)
        t2 = np.tan((s - a) / 2.0)
        t3 = np.tan((s - b) / 2.0)
        t4 = np.tan((s - c) / 2.0)
        prod = np.clip(t1 * t2 * t3 * t4, 0.0, None)
        E_over4 = np.arctan(np.sqrt(prod))
        return 4.0 * E_over4  # steradians

    def spherical_quad_area_sr(lon00, lat00, lon10, lat10, lon01, lat01, lon11, lat11):
        """
        Compute spherical quadrilateral area by splitting into two triangles.

        Parameters
        ----------
        lonXY, latXY : ndarray
            Corner coordinates in radians.

        Returns
        -------
        ndarray
            Quadrilateral area in steradians.
        """
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
    time_step: float = 1,
    time_integrate: float = None,
    ra_range: list = [0, 360],
    dec_range: list = [-90, 90],
    ra_res: float = 0.5,
    dec_res: float = 0.5,
    verbose: bool = True,
    force_compute: bool = False,
):
    """ """

    exposure_map_dict = calc_exposure_maps(
        time_range=time_range,
        time_zone=time_zone,
        time_step=time_step,
        ra_range=ra_range,
        dec_range=dec_range,
        ra_res=ra_res,
        dec_res=dec_res,
        time_integrate=time_integrate,
        verbose=verbose,
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
    exp_total = exp_maps.sum(axis=0)  # shape is (len(ra_arr), len(dec_arr))

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
    galactic_counts = bg * exp_at_centers * area_arcmin2  # units: counts

    out = {
        "galactic_counts": galactic_counts,  # same shape as background (Ny_bg, Nx_bg)
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
                "galactic_counts": "count",
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

    # Return in ascending order
    return edges


def implement_background_correction(
    counts_dict: dict,
    lexi_df: pd.DataFrame,
) -> dict:
    """
    Given a dictionary of background counts per pixel and a LEXI event dataframe,
    compute the LEXI histogram and subtract the expected background counts per pixel.

    Parameters
    ----------
    counts_dict : dict
        Dictionary containing:
          - ra_center_map (2D array): RA coordinates of pixel centers [deg].
          - dec_center_map (2D array): Dec coordinates of pixel centers [deg].
          - background_counts_per_s_per_arcmin2 (2D array): Background rate [cnt/s/arcmin^2].
          - pixel_area_arcmin2 (2D array): Pixel area [arcmin^2].
          - exposure_at_centers_sec (2D array): Exposure time at pixel centers [s].
          - time_range (list): [start_time, end_time] of the observation.
    lexi_df : pandas.DataFrame
        DataFrame containing LEXI photon events with columns:
          - "photon_RA": Photon Right Ascension [deg].
          - "photon_Dec": Photon Declination [deg].

    Returns
    -------
    result_dict : dict
        Dictionary containing:
          - "lexi_histogram": 2D array of LEXI event counts per pixel before background correction.
          - "expected_background": 2D array of expected background counts per pixel.
          - "background_corrected_histogram": 2D array of background-corrected LEXI counts per pixel (clipped at zero).
          - "expected_background_rate": 2D array of expected background rate per pixel [cnt/s].

    NOTE: The unit of all the counts arrays included in the returned dictionary is simply "counts /
    pixel" (cnts/pixel).
    """

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
        lexi_histogram = np.zeros((H, W), dtype=float)
    else:
        # --- Histogram: rows index RA bins, columns index Dec bins ---
        # Note: numpy.histogram2d takes (x, y, bins=[x_edges, y_edges]) and returns H[xbin, ybin]
        H_raw, _, _ = np.histogram2d(ra_ev, dec_ev, bins=[ra_edges, dec_edges])
        # H_raw.shape == (len(ra_edges)-1, len(dec_edges)-1) = (H, W)
        lexi_histogram = H_raw.astype(float)

    # --- Galactic background: Expected counts per pixel ---
    # Units: (cnt/s/arcmin^2) * (arcmin^2) * (s) = counts
    expected_galactic_bg = bg_rate * pix_area * expos

    # --- Dark background: Expected counts per pixel ---
    # Must normalize by pixel area to ensure unit consistency with galactic background
    central_epoch = (
        pd.to_datetime(counts_dict["time_range"][0])
        + (
            pd.to_datetime(counts_dict["time_range"][1])
            - pd.to_datetime(counts_dict["time_range"][0])
        )
        / 2
    )
    ra_dark, dec_dark, dark_time_interval = gffd.get_dark_background(central_epoch=central_epoch)

    ra_dark = np.asarray(ra_dark, dtype=float) + 2
    dec_dark = np.asarray(dec_dark, dtype=float)
    m = np.isfinite(ra_dark) & np.isfinite(dec_dark)
    ra_dark, dec_dark = ra_dark[m], dec_dark[m]
    # 2D histogram in (RA, Dec) using the SAME edges as LEXI
    if ra_dark.size == 0:
        dark_bgnd_hist = np.zeros((H, W), dtype=float)
    else:
        H_dark, _, _ = np.histogram2d(ra_dark, dec_dark, bins=[ra_edges, dec_edges])
    dark_bgnd_hist = H_dark.astype(float)

    # Convert to rate (cnt/s/arcmin^2) using the time interval over which the dark background
    # was accumulated AND normalizing by pixel area to match the galactic background units
    dark_bgnd_hist_rate = dark_bgnd_hist / (dark_time_interval * pix_area)
    # Convert to expected counts using the exposure map and pixel area
    # Rate (cnt/s/arcmin^2) * area (arcmin^2) * exposure (s) = counts
    dark_bgnd_hist_counts = dark_bgnd_hist_rate * pix_area * expos

    expected_bg = expected_galactic_bg + dark_bgnd_hist_counts
    expected_bg_rate = expected_bg / expos  # cnt/s
    # Print all the statistics (mean, median, std, min, max) of expected_galactic_bg,
    # dark_bgnd_hist_counts, expected_bg in a table
    headers = ["Statistic", "Galactic BG", "Dark BG", "Total BG"]
    table = [
        [
            "Mean",
            np.mean(expected_galactic_bg),
            np.mean(dark_bgnd_hist_counts),
            np.mean(expected_bg),
        ],
        [
            "Median",
            np.median(expected_galactic_bg),
            np.median(dark_bgnd_hist_counts),
            np.median(expected_bg),
        ],
        ["Std", np.std(expected_galactic_bg), np.std(dark_bgnd_hist_counts), np.std(expected_bg)],
        ["Min", np.min(expected_galactic_bg), np.min(dark_bgnd_hist_counts), np.min(expected_bg)],
        ["Max", np.max(expected_galactic_bg), np.max(dark_bgnd_hist_counts), np.max(expected_bg)],
        [
            "Total Counts",
            np.nansum(expected_galactic_bg),
            np.nansum(dark_bgnd_hist_counts),
            np.nansum(expected_bg),
        ],
        [
            "Count rate (cnt/s)",
            np.nansum(expected_galactic_bg / expos),
            np.nansum(dark_bgnd_hist_counts / expos),
            np.nansum(expected_bg_rate),
        ],
    ]
    print("\nExpected Background Statistics:")
    print(tabulate.tabulate(table, headers=headers))
    ##############
    # --- Background-corrected histogram ---
    lexi_bgnd_corrected = lexi_histogram - expected_bg

    # Print statistics of the raw LEXI histogram and background-corrected histogram
    headers2 = ["Statistic", "LEXI Raw", "LEXI BGnd-Corrected"]
    table2 = [
        ["Mean", np.mean(lexi_histogram), np.mean(lexi_bgnd_corrected)],
        ["Median", np.median(lexi_histogram), np.median(lexi_bgnd_corrected)],
        ["Std", np.std(lexi_histogram), np.std(lexi_bgnd_corrected)],
        ["Min", np.min(lexi_histogram), np.min(lexi_bgnd_corrected)],
        ["Max", np.max(lexi_histogram), np.max(lexi_bgnd_corrected)],
        ["Total Counts", np.nansum(lexi_histogram), np.nansum(lexi_bgnd_corrected)],
        [
            "Count rate (cnt/s)",
            np.nansum(lexi_histogram) / 300.0,
            np.nansum(lexi_bgnd_corrected) / 300.0,
        ],
    ]
    print("\nLEXI Histogram Statistics:")
    print(tabulate.tabulate(table2, headers=headers2))
    print("\n")

    # Clip negatives to zero (no physical negative counts after subtraction)
    lexi_bgnd_corrected = np.clip(lexi_bgnd_corrected, 0.0, None)

    # Add results to output dict
    results = counts_dict.copy()
    results.update(
        {
            "lexi_histogram_raw": lexi_histogram,
            "expected_galactic_bg_counts": expected_galactic_bg,
            "expected_dark_bg_counts": dark_bgnd_hist_counts,
            "expected_bg_counts": expected_bg,
            "lexi_hist_bgnd_corrected": lexi_bgnd_corrected,
            "ra_edges": ra_edges,
            "dec_edges": dec_edges,
        }
    )

    return results


def implement_flat_field_correction(
    counts_dict: dict,
    *,
    min_ff_norm: float = 0.05,  # floor to avoid huge division (set to 0 to disable)
    epsilon: float = 1e-12,  # numerical safety
) -> dict:
    """
    Build a flat-field map on the same RA/Dec grid as `lexi_result['lexi_histogram']`,
    normalize it to max=1, and divide the LEXI histogram by it.

    Parameters
    ----------
    counts_dict : dict
        Must contain 'ra_center_map' and 'dec_center_map' (HxW).
    lexi_result : dict
        Output of compute_lexi_histograms(...), must include:
          'lexi_histogram', 'ra_edges', 'dec_edges'
    flat_field_file : str
        Path to CDF containing variables 'photon_RA' and 'photon_Dec' (degrees).
    min_ff_norm : float
        Floor for the normalized flat-field map (after normalization to max=1).
        This prevents division blow-ups in underexposed bins.
    epsilon : float
        Small number to keep denominators non-zero.

    Returns
    -------
    out : dict with keys
    """
    # --- grid from counts_dict / lexi_result
    ra_map = np.asarray(counts_dict["ra_center_map"], dtype=float)
    # dec_map = np.asarray(counts_dict["dec_center_map"], dtype=float)
    H, W = ra_map.shape

    ra_edges = counts_dict.get("ra_edges")
    dec_edges = counts_dict.get("dec_edges")

    # --- read flat-field events
    # Works with either SpacePy (pycdf) or cdflib; adapt import as you use.

    # Get the mid point of the time_range
    start = counts_dict["time_range"][0]
    end = counts_dict["time_range"][1]
    central_epoch = start + (end - start) / 2
    ra_ff, dec_ff = gffd.fast_transform_fixed_epoch(central_epoch=central_epoch)
    ra_ff = np.asarray(ra_ff, dtype=float) + 2
    dec_ff = np.asarray(dec_ff, dtype=float)
    # Clean NaNs
    m = np.isfinite(ra_ff) & np.isfinite(dec_ff)
    ra_ff, dec_ff = ra_ff[m], dec_ff[m]

    # --- 2D histogram in (RA, Dec) using the SAME edges as LEXI
    if ra_ff.size == 0:
        flat_field_hist = np.zeros((H, W), dtype=float)
    else:
        Hff, _, _ = np.histogram2d(ra_ff, dec_ff, bins=[ra_edges, dec_edges])
        flat_field_hist = Hff.astype(float)  # shape (H, W)

    # --- normalize to max=1
    # max_ff = flat_field_hist.max() if flat_field_hist.size else 0.0
    ff_0 = flat_field_hist[flat_field_hist != 0]
    ff_mode = scipy.stats.mode(ff_0, axis=None, keepdims=False).mode if ff_0.size else 0.0
    if ff_mode > 0:
        flat_field_hist_norm = flat_field_hist / ff_mode
    else:
        flat_field_hist_norm = np.zeros_like(flat_field_hist, dtype=float)
    # Optional floor to avoid exploding corrections where the FF is ~0
    # if min_ff_norm is not None and min_ff_norm > 0:
    #     flat_field_hist_norm = np.maximum(flat_field_hist_norm, float(min_ff_norm))

    # --- LEXI histogram
    lexi_histogram = np.asarray(counts_dict["lexi_histogram_raw"], dtype=float)

    # --- flat-field corrected: divide counts by normalized FF
    lexi_flat_corrected_hist = lexi_histogram / (flat_field_hist_norm + epsilon)

    results = counts_dict.copy()
    results.update(
        {
            "flat_field_hist": flat_field_hist,
            "flat_field_hist_norm": flat_field_hist_norm,
            "lexi_histogram": lexi_histogram,
            "lexi_flat_corrected_hist": lexi_flat_corrected_hist,
        }
    )

    return results


def save_lexi_results(
    data: dict, output_dir: str = "/mnt/cephadrius/bu_research/lexi_data/l2/1min"
):

    selected_data = {}

    selected_data["exposure_map"] = data["exposure_at_centers_sec"]
    selected_data["cosmic_background_map"] = data["expected_galactic_bg_counts"]
    selected_data["dark_background_map"] = data["expected_dark_bg_counts"]
    selected_data["total_background_map"] = data["expected_bg_counts"]
    selected_data["pixel_area"] = data["pixel_area_arcmin2"]
    selected_data["lexi_image"] = data["lexi_histogram_raw"] / data["exposure_at_centers_sec"][:, :]
    selected_data["lexi_image_background_corrected"] = (
        data["lexi_hist_bgnd_corrected"] / data["exposure_at_centers_sec"][:, :]
    )

    # Selected keys
    selected_keys = [
        # "exposure_map",
        "pixel_area",
        "cosmic_background_map",
        "dark_background_map",
        "total_background_map",
        "lexi_image",
        "lexi_image_background_corrected",
    ]

    # Create a mask of bins where exposure is greater than zero, and only select those bins
    exposure_mask = selected_data["exposure_map"] <= 0
    for k in selected_keys:
        selected_data[k] = np.where(exposure_mask, -1.0e31, selected_data[k])

    selected_data["epoch_start"] = data["time_range"][0].to_pydatetime()
    selected_data["epoch_end"] = data["time_range"][1].to_pydatetime()
    selected_data["ra_bin"] = 0.5 * (data["ra_edges"][:-1] + data["ra_edges"][1:])
    selected_data["dec_bin"] = 0.5 * (data["dec_edges"][:-1] + data["dec_edges"][1:])
    selected_data["ra_bin_map"] = data["ra_center_map"]
    selected_data["dec_bin_map"] = data["dec_center_map"]

    # Get the az-el epoch as the time between the start and end times
    az_el_epoch = (
        data["time_range"][0] + (data["time_range"][1] - data["time_range"][0]) / 2
    ).to_pydatetime()
    # Convert RA/Dec bin edges to azimuth/elevation bin edges
    az_bin_edges, el_bin_edges = cradecazel.radec_to_azel_array(
        ra_array=data["ra_edges"], dec_array=data["dec_edges"], epoch=az_el_epoch
    )
    selected_data["az_bin"] = 0.5 * (az_bin_edges[:-1] + az_bin_edges[1:])
    selected_data["el_bin"] = 0.5 * (el_bin_edges[:-1] + el_bin_edges[1:])
    selected_data["az_bin_map"], selected_data["el_bin_map"] = cradecazel.radec_to_azel_grid(
        ra_grid=data["ra_center_map"],
        dec_grid=data["dec_center_map"],
        epoch=az_el_epoch,
    )
    # Declare the data types for each variable
    data_format_dict_lexi_l2 = {
        "ra_bin": np.float32,
        "dec_bin": np.float32,
        "ra_bin_map": np.float32,
        "dec_bin_map": np.float32,
        "az_bin": np.float32,
        "el_bin": np.float32,
        "az_bin_map": np.float32,
        "el_bin_map": np.float32,
        "pixel_area": np.float32,
        "exposure_map": np.float32,
        "cosmic_background_map": np.float32,
        "dark_background_map": np.float32,
        "total_background_map": np.float32,
        "lexi_image": np.float32,
        "lexi_image_background_corrected": np.float32,
    }
    formatted_selected_data = {}
    for k in data_format_dict_lexi_l2.keys():
        formatted_selected_data[k] = selected_data[k].astype(data_format_dict_lexi_l2[k])
    formatted_selected_data["epoch_start"] = selected_data["epoch_start"]
    formatted_selected_data["epoch_end"] = selected_data["epoch_end"]
    # return formatted_selected_data
    cdf_file = sdtc.save_data_to_cdf(
        data=formatted_selected_data,
        output_dir=output_dir,
    )
    return cdf_file


delta_v = 5  # degree
start_time = "2025-03-16 19:00:00"
end_time = "2025-03-16 21:15:00"
read_all_lexi = True
if read_all_lexi:
    # Read all L1c data files in the time range
    all_lexi_df = gl1c.read_all_data_files(
        file_list=None,
        start_time=start_time,
        end_time=end_time,
        return_data_type="dataframe",
        kwargs={
            "data_folder_location": "/media/cephadrius/lexi_data/lexi_data/L1c/sci/cdf",
            "version": "latest",
            "start_time": start_time,
            "end_time": end_time,
        },
    )

delta_time_minutes = 5
time_ranges = pd.date_range(start=start_time, end=end_time, freq=f"{delta_time_minutes}min")
time_ranges = [(str(t), str(t + pd.Timedelta(delta_time_minutes, unit="m"))) for t in time_ranges][
    :-1
]
spc_df = pd.read_csv(
    "../data/pointing/lexi_look_direction_data_resampled_interpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
)
spc_df["RA"] = spc_df["ra_lexi"]
spc_df["DEC"] = spc_df["dec_lexi"]

# Set Epoch as index and convert to datetime
spc_df["Epoch"] = pd.to_datetime(spc_df["Epoch"], utc=True)
spc_df.set_index("Epoch", inplace=True)

recompute = True
for start, end in time_ranges[:]:
    if recompute:
        # Select the dataframe within the time range
        time_range = pd.to_datetime([start, end], utc=True)
        selected_spc_df = spc_df.loc[time_range[0] : time_range[1]]
        ra_center = selected_spc_df["RA"].median()
        dec_center = selected_spc_df["DEC"].median()

        input_params = {
            "time_range": [start, end],
            # "time_integrate": 600,  # 2 hours
            "ra_res": 0.1,
            "dec_res": 0.1,
            "ra_range": [ra_center - delta_v, ra_center + delta_v],
            "dec_range": [dec_center - delta_v, dec_center + delta_v],
            "verbose": True,
            "force_compute": True,
        }

        exposure_maps_dict, sky_bgnds_dict = calc_sky_backgrounds(
            **input_params,
            # reducer=np.mean,
            # strict_consecutive=False,
        )

        org_counts_dict = background_counts_from_exposure(exposure_maps_dict, sky_bgnds_dict)
        # counts_dict = org_counts_dict.copy()
        lexi_df = all_lexi_df.loc[
            (all_lexi_df.index >= pd.to_datetime(start, utc=True))
            & (all_lexi_df.index < pd.to_datetime(end, utc=True))
        ]
        bgnd_counts_dict = implement_background_correction(
            counts_dict=org_counts_dict, lexi_df=lexi_df
        )

        # counts_dict = implement_flat_field_correction(counts_dict=bgnd_counts_dict)

        # #

        cdf_file = save_lexi_results(
            data=bgnd_counts_dict,
            output_dir=f"/mnt/cephadrius/bu_research/lexi_data/l2/{delta_time_minutes}min/",
        )
