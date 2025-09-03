import importlib
import shutil
from pathlib import Path

import get_l2_files as gl2f
import get_lexi_l1c_data as gl1c
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

importlib.reload(gl2f)
importlib.reload(gl1c)

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
from matplotlib.ticker import ScalarFormatter


def centers_to_corners_2d(ra_c, dec_c):
    """
    ra_c, dec_c: (H, W) center maps in degrees.
    Returns: RAcorn, DECcorn with shape (H+1, W+1) for pcolormesh.
    Uses midpoint edges and linear extrapolation at boundaries.
    """
    ra_c = np.asarray(ra_c, float)
    dec_c = np.asarray(dec_c, float)
    H, W = ra_c.shape

    # Midpoints between adjacent centers (internal edges)
    ra_i = 0.5 * (ra_c[1:, :] + ra_c[:-1, :])  # (H-1, W)
    ra_j = 0.5 * (ra_c[:, 1:] + ra_c[:, :-1])  # (H, W-1)
    dec_i = 0.5 * (dec_c[1:, :] + dec_c[:-1, :])
    dec_j = 0.5 * (dec_c[:, 1:] + dec_c[:, :-1])

    # Extrapolate outer edges along i (rows)
    ra_top = ra_c[0, :] - (ra_i[0, :] - ra_c[0, :])
    ra_bot = ra_c[-1, :] + (ra_c[-1, :] - ra_i[-1, :])
    dec_top = dec_c[0, :] - (dec_i[0, :] - dec_c[0, :])
    dec_bot = dec_c[-1, :] + (dec_c[-1, :] - dec_i[-1, :])

    # Extrapolate outer edges along j (cols)
    ra_left = ra_c[:, 0] - (ra_j[:, 0] - ra_c[:, 0])
    ra_right = ra_c[:, -1] + (ra_c[:, -1] - ra_j[:, -1])
    dec_left = dec_c[:, 0] - (dec_j[:, 0] - dec_c[:, 0])
    dec_right = dec_c[:, -1] + (dec_c[:, -1] - dec_j[:, -1])

    # Build (H+1, W+1) corners by averaging edges appropriately
    RAcorn = np.empty((H + 1, W + 1), float)
    DECcorn = np.empty((H + 1, W + 1), float)

    # Internal corners
    RAcorn[1:H, 1:W] = 0.25 * (ra_c[:-1, :-1] + ra_c[1:, :-1] + ra_c[:-1, 1:] + ra_c[1:, 1:])
    DECcorn[1:H, 1:W] = 0.25 * (dec_c[:-1, :-1] + dec_c[1:, :-1] + dec_c[:-1, 1:] + dec_c[1:, 1:])

    # Edges (average adjacent edge lines with neighbors)
    RAcorn[0, 1:W] = 0.5 * (ra_top[:-1] + ra_top[1:])
    RAcorn[-1, 1:W] = 0.5 * (ra_bot[:-1] + ra_bot[1:])
    RAcorn[1:H, 0] = 0.5 * (ra_left[:-1] + ra_left[1:])
    RAcorn[1:H, -1] = 0.5 * (ra_right[:-1] + ra_right[1:])

    DECcorn[0, 1:W] = 0.5 * (dec_top[:-1] + dec_top[1:])
    DECcorn[-1, 1:W] = 0.5 * (dec_bot[:-1] + dec_bot[1:])
    DECcorn[1:H, 0] = 0.5 * (dec_left[:-1] + dec_left[1:])
    DECcorn[1:H, -1] = 0.5 * (dec_right[:-1] + dec_right[1:])

    # Four corners (average of adjacent edges)
    RAcorn[0, 0] = 0.5 * (ra_top[0] + ra_left[0])
    RAcorn[0, -1] = 0.5 * (ra_top[-1] + ra_right[0])
    RAcorn[-1, 0] = 0.5 * (ra_bot[0] + ra_left[-1])
    RAcorn[-1, -1] = 0.5 * (ra_bot[-1] + ra_right[-1])

    DECcorn[0, 0] = 0.5 * (dec_top[0] + dec_left[0])
    DECcorn[0, -1] = 0.5 * (dec_top[-1] + dec_right[0])
    DECcorn[-1, 0] = 0.5 * (dec_bot[0] + dec_left[-1])
    DECcorn[-1, -1] = 0.5 * (dec_bot[-1] + dec_right[-1])

    return RAcorn, DECcorn


def plot_on_ra_dec(ax, ra_corners, dec_corners, data, title, vmin=None, vmax=None, norm="linear"):
    if norm == "linear":
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    elif norm == "log":
        if vmin is None:
            if np.nanmin(data) > 0:
                vmin = np.nanmin(data)
            else:
                vmin = 1e-3 * np.nanmax(data)
        if vmax is None:
            vmax = np.nanmax(data)
        norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
    else:
        norm = None
    pm = ax.pcolormesh(
        ra_corners,
        dec_corners,
        data,
        shading="auto",
        # vmin=vmin,
        # vmax=vmax,
        cmap="plasma",
        norm=norm,
    )
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_title(title)

    spc_df = pd.read_csv(
        "../data/pointing/lexi_look_direction_data_resampled_interpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
    )
    spc_df["RA"] = spc_df["ra_lexi"]
    spc_df["DEC"] = spc_df["dec_lexi"]

    # Set Epoch as index and convert to datetime
    spc_df["Epoch"] = pd.to_datetime(spc_df["Epoch"], utc=True)
    spc_df.set_index("Epoch", inplace=True)
    # Select the dataframe within the time range
    time_range = pd.to_datetime(input_params["time_range"], utc=True)
    spc_df = spc_df.loc[time_range[0] : time_range[1]]
    ra_center = spc_df["RA"].median()
    dec_center = spc_df["DEC"].median()
    ax.set_aspect("equal", adjustable="box")
    circle = plt.Circle((ra_center, dec_center), 4.55, color="white", fill=False)
    # Put a dot at the center
    ax.plot(ra_center, dec_center, marker="o", color="k", markersize=5)
    # Add an annotation with the center coordinates
    ax.annotate(
        f"({ra_center:.2f}, {dec_center:.2f})",
        (ra_center + 0.5, dec_center + 0.5),
        color="white",
        fontsize=12,
        weight="bold",
        bbox=dict(facecolor="black", alpha=0.5, pad=2),
    )

    ax.add_artist(circle)
    ax.set_aspect("equal")
    cbar = plt.colorbar(pm, ax=ax, label=title, orientation="vertical", fraction=0.046, pad=0.00)

    # Force scientific notation with offset at the top
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    # formatter.set_powerlimits((-1, 1))  # force sci notation outside [-1e-3, 1e3]
    cbar.ax.yaxis.set_major_formatter(formatter)
    # Hide minor ticks
    cbar.ax.yaxis.set_minor_formatter(plt.NullFormatter())

    # Move the offset (×10^n) to the top of the colorbar
    cbar.ax.yaxis.get_offset_text().set(size=14)  # font size if you like
    cbar.ax.yaxis.get_offset_text().set_position((1.15, 1))
    return pm


def overlay_ra_dec_contours(ax, ra_c, dec_c, n_ra=7, n_dec=7, **kw):
    ra_levels = np.linspace(np.nanmin(ra_c), np.nanmax(ra_c), n_ra)
    dec_levels = np.linspace(np.nanmin(dec_c), np.nanmax(dec_c), n_dec)
    ax.contour(
        ra_c, levels=ra_levels, colors="k", linewidths=0.5, alpha=0.4, extent=None
    )  # drawn in pixel coords for quick look
    ax.contour(dec_c, levels=dec_levels, colors="w", linewidths=0.5, alpha=0.4, extent=None)


delta_v = 5  # degree
start_time = "2025-03-16 19:00:00"
end_time = "2025-03-16 21:15:00"
read_all_lexi = False
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
for start, end in time_ranges[:1]:
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

        exposure_maps_dict, sky_bgnds_dict = gl2f.calc_sky_backgrounds(
            **input_params,
            # reducer=np.mean,
            # strict_consecutive=False,
        )

        org_counts_dict = gl2f.background_counts_from_exposure(exposure_maps_dict, sky_bgnds_dict)
        # counts_dict = org_counts_dict.copy()
        lexi_df = all_lexi_df.loc[
            (all_lexi_df.index >= pd.to_datetime(start, utc=True))
            & (all_lexi_df.index < pd.to_datetime(end, utc=True))
        ]
        bgnd_counts_dict = gl2f.implement_background_correction(
            counts_dict=org_counts_dict, lexi_df=lexi_df
        )

        counts_dict = gl2f.implement_flat_field_correction(counts_dict=bgnd_counts_dict)

        cdf_file = gl2f.save_lexi_results(
            data=counts_dict,
        )
        # Wherever exposure is zero, set all different counts to NaN
        mask = counts_dict["exposure_at_centers_sec"] <= 0
        for key in [
            "counts_map",
            "exposure_at_centers_sec",
            "background_counts_per_s_per_arcmin2",
            "pixel_area_arcmin2",
            "flat_field_hist",
            "flat_field_hist_norm",
            "lexi_hist_raw",
            "lexi_hist_bgnd_corrected",
            "lexi_flat_corrected_hist",
            "expected_bg_counts",
        ]:
            counts_dict[key] = np.where(mask, np.nan, counts_dict[key])

        # Make a 2 by 2 grid of plots
        # fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        ra_c = counts_dict["ra_center_map"]
        dec_c = counts_dict["dec_center_map"]
        RAcorn, DECcorn = centers_to_corners_2d(ra_c, dec_c)

        counts = counts_dict["counts_map"]
        expo = counts_dict["exposure_at_centers_sec"]
        bgrt = counts_dict["background_counts_per_s_per_arcmin2"]
        area = counts_dict["pixel_area_arcmin2"]
        lexi_hist = counts_dict["lexi_hist_raw"]
        lexi_bgnd_corrected = counts_dict["lexi_hist_bgnd_corrected"]
        expected_bg = counts_dict["expected_bg_counts"]
        flat_field = counts_dict["flat_field_hist"]
        flat_field_norm = counts_dict["flat_field_hist_norm"]
        lexi_flat_field_corrected = counts_dict["lexi_flat_corrected_hist"]

        expected_bg_counts = bgrt * area * expo

    # Plot the exposure maps and counts
    fig, axs = plt.subplots(3, 3, figsize=(20, 16), constrained_layout=True)
    # Set the hspace and wspace
    fig.subplots_adjust(hspace=0.0, wspace=0.0)
    # Set the default font size
    mpl.rcParams.update({"font.size": 16})

    # Set the same vmin and vmax for lexi_hist and lexi_bgnd_corrected
    # vmin_lexi = np.nanmin(
    #     [np.nanmin(lexi_hist), np.nanmin(lexi_bgnd_corrected), np.nanmin(lexi_flat_field_corrected)]
    # )
    # vmax_lexi = np.nanmax(
    #     [np.nanmax(lexi_hist), np.nanmax(lexi_bgnd_corrected), np.nanmax(lexi_flat_field_corrected)]
    # )
    # if vmin_lexi <= 0:
    #     vmin_lexi = 1e-1 * vmax_lexi
    vmin_lexi = 1
    vmax_lexi = 30

    plot_on_ra_dec(
        axs[0, 0],
        RAcorn,
        DECcorn,
        bgrt,
        "Background Counts (cts/s/arcmin$^2$)",
        vmin=1e-6,
        vmax=1e-5,
        norm="log",
    )
    plot_on_ra_dec(
        axs[0, 1], RAcorn, DECcorn, expo, "Exposure (s)", norm="log", vmin=1e-1, vmax=3.3e2
    )
    plot_on_ra_dec(
        axs[0, 2],
        RAcorn,
        DECcorn,
        counts,
        "Total Background Counts",
        norm="log",
        vmin=1e-3,
        vmax=1e-1,
    )
    plot_on_ra_dec(
        axs[1, 0], RAcorn, DECcorn, area, "Pixel Area (arcmin$^2$)", norm="linear", vmin=35, vmax=36
    )
    plot_on_ra_dec(
        axs[1, 1],
        RAcorn,
        DECcorn,
        lexi_hist,
        "Lexi Histogram (Raw)",
        vmin=vmin_lexi,
        vmax=vmax_lexi,
        norm="log",
    )
    plot_on_ra_dec(
        axs[1, 2],
        RAcorn,
        DECcorn,
        lexi_bgnd_corrected,
        "Lexi Histogram (Bgnd Corrected)",
        vmin=vmin_lexi,
        vmax=vmax_lexi,
        norm="log",
    )

    plot_on_ra_dec(
        axs[2, 0], RAcorn, DECcorn, flat_field, "Flat Field", norm="log", vmin=1e2, vmax=7e2
    )
    plot_on_ra_dec(
        axs[2, 1],
        RAcorn,
        DECcorn,
        flat_field_norm,
        "Normalized Flat Field",
        norm="log",
        vmin=1e-1,
        vmax=1e0,
    )
    plot_on_ra_dec(
        axs[2, 2],
        RAcorn,
        DECcorn,
        lexi_flat_field_corrected,
        "Lexi Histogram (Bgnd + Flat Field Corrected)",
        vmin=vmin_lexi,
        vmax=vmax_lexi,
        norm="log",
    )
    for ax in axs.flat:
        ax.contour(RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="c", linewidths=0.6, alpha=0.5)
        ax.contour(
            RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="k", linewidths=0.6, alpha=0.5
        )
        ax.set_aspect("equal", adjustable="box")

    # plt.tight_layout()
    figure_path = Path(f"../figures/exposure_maps/bg_corrected/shifted/{delta_time_minutes}min/")
    figure_path.mkdir(parents=True, exist_ok=True)
    fig_name = (
        input_params["time_range"][0].replace(" ", "_").replace(":", "")
        + "_to_"
        + input_params["time_range"][1].replace(" ", "_").replace(":", "")
        + "_exposure_maps.png"
    )
    fig.savefig(figure_path / fig_name, dpi=150, bbox_inches="tight", pad_inches=0.1)
    # plt.show()
    plt.close()

    """
    # Plot the lexi_hist
    fig, ax = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    aa = ax.pcolormesh(
        RAcorn, DECcorn, lexi_hist, shading="auto", cmap="plasma", vmin=vmin_lexi, vmax=vmax_lexi
    )
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_title("lexi_hist")
    plt.colorbar(aa, label="Counts", ax=ax)
    plt.savefig("lexi_hist.png", dpi=150)
    plt.close()

    # Plot the lexi_bgnd_corrected
    fig, ax = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    aa = ax.pcolormesh(
        RAcorn,
        DECcorn,
        lexi_bgnd_corrected,
        shading="auto",
        cmap="plasma",
        vmin=vmin_lexi,
        vmax=vmax_lexi,
    )
    ax.set_xlabel("RA (deg)")
    ax.set_ylabel("Dec (deg)")
    ax.set_title("lexi_bgnd_corrected")
    plt.colorbar(aa, label="Counts", ax=ax)
    plt.savefig("lexi_bgnd_corrected.png", dpi=150)
    plt.close()
    """
