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


def plot_on_ra_dec(ax, ra_corners, dec_corners, data, title, vmin=None, vmax=None):
    pm = ax.pcolormesh(
        ra_corners, dec_corners, data, shading="auto", vmin=vmin, vmax=vmax, cmap="plasma"
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
        fontsize=8,
        weight="bold",
        bbox=dict(facecolor="black", alpha=0.5, pad=2),
    )

    ax.add_artist(circle)
    ax.set_aspect("equal")
    plt.colorbar(pm, ax=ax, label=title)
    return pm


def overlay_ra_dec_contours(ax, ra_c, dec_c, n_ra=7, n_dec=7, **kw):
    ra_levels = np.linspace(np.nanmin(ra_c), np.nanmax(ra_c), n_ra)
    dec_levels = np.linspace(np.nanmin(dec_c), np.nanmax(dec_c), n_dec)
    ax.contour(
        ra_c, levels=ra_levels, colors="k", linewidths=0.5, alpha=0.4, extent=None
    )  # drawn in pixel coords for quick look
    ax.contour(dec_c, levels=dec_levels, colors="w", linewidths=0.5, alpha=0.4, extent=None)


array_to_image_kwargs_exp = {
    "x_range": [190, 240],
    "y_range": [-30, -10],
    "x_lim": [220, 240],
    "y_lim": [-30, -15],
    "cmap": "plasma",
    "cmin": 1,
    "norm": None,
    "norm_type": "linear",
    "aspect": "equal",
    "figure_title": "LEXI Exposure Map",
    "show_colorbar": True,
    "cbar_label": "Seconds",
    "cbar_orientation": "vertical",
    "show_axes": True,
    "figure_size": (5, 5),
    "figure_format": "png",
    "figure_font_size": 12,
    "save": True,
    "save_name": "default",
    "save_path": None,
    "dpi": 300,
    "dark_mode": True,
    "verbose": True,
    "display": True,
}
delta_v = 5.5  # degree
start_time = "2025-03-16 19:00:00"
end_time = "2025-03-16 21:15:00"
delta_time_minutes = 5
time_ranges = pd.date_range(start=start_time, end=end_time, freq=f"{delta_time_minutes}min")
time_ranges = [(str(t), str(t + pd.Timedelta(delta_time_minutes, unit="m"))) for t in time_ranges][
    :-1
]
recompute = False
for start, end in time_ranges[:1]:
    if recompute:
        input_params = {
            "time_range": [start, end],
            # "time_integrate": 600,  # 2 hours
            "ra_res": 0.1,
            "dec_res": 0.1,
            "ra_range": [15.4 - delta_v, 15.4 + delta_v],
            "dec_range": [14 - delta_v, 14 + delta_v],
            # "save_exposure_map_file": True,
            # "save_exposure_map_image": True,
            # "save_sky_backgrounds_file": True,
            # "save_sky_backgrounds_image": False,
            # "save_lexi_images": True,
            "verbose": True,
            # "background_correction_on": True,
            # "array_to_image_kwargs": array_to_image_kwargs_exp,
            "force_compute": True,
        }

        # all_data_dict = gl1c.read_all_data_files(start_time=start, end_time=end)
        exposure_maps_dict, sky_bgnds_dict = gl2f.calc_sky_backgrounds(
            **input_params,
            # reducer=np.mean,
            # strict_consecutive=False,
        )

        org_counts_dict = gl2f.background_counts_from_exposure(exposure_maps_dict, sky_bgnds_dict)
        # counts_dict = org_counts_dict.copy()
        counts_dict = gl2f.implement_background_correction(counts_dict=org_counts_dict)
        # Wherever exposure is zero, set counts to NaN (no data)
        counts_dict["exposure_at_centers_sec"] = np.where(
            counts_dict["exposure_at_centers_sec"] > 0,
            counts_dict["exposure_at_centers_sec"],
            np.nan,
        )
        counts_dict["counts_map"] = np.where(
            counts_dict["exposure_at_centers_sec"] > 0,
            counts_dict["counts_map"],
            np.nan,
        )

        keys_to_plot = [
            "counts_map",
            "exposure_at_centers_sec",
            "background_counts_per_s_per_arcmin2",
            "pixel_area_arcmin2",
        ]

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

        # Make a 2 by 2 grid of plots
        # fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        ra_c = org_counts_dict["ra_center_map"]
        dec_c = org_counts_dict["dec_center_map"]
        RAcorn, DECcorn = centers_to_corners_2d(ra_c, dec_c)

        counts = org_counts_dict["counts_map"]
        expo = org_counts_dict["exposure_at_centers_sec"]
        bgrt = org_counts_dict["background_counts_per_s_per_arcmin2"]
        area = org_counts_dict["pixel_area_arcmin2"]
        lexi_hist = org_counts_dict["lexi_hist_raw"]
        lexi_bgnd_corrected = counts_dict["lexi_hist_bgnd_corrected"]
        expected_bg = org_counts_dict["expected_bg_counts"]

        expected_bg_counts = bgrt * area * expo

    fig, axs = plt.subplots(2, 2, figsize=(11, 9), constrained_layout=True)

    # Set the same vmin and vmax for lexi_hist and lexi_bgnd_corrected
    vmin_lexi = np.min([np.nanmin(lexi_hist), np.nanmin(lexi_bgnd_corrected)])
    vmax_lexi = np.max([np.nanmax(lexi_hist), np.nanmax(lexi_bgnd_corrected)])

    plot_on_ra_dec(axs[0, 0], RAcorn, DECcorn, counts, "counts_map")
    plot_on_ra_dec(
        axs[0, 1], RAcorn, DECcorn, lexi_hist, "lexi_hist", vmin=vmin_lexi, vmax=vmax_lexi
    )
    plot_on_ra_dec(axs[1, 0], RAcorn, DECcorn, bgrt, "background_counts_per_s_per_arcmin2")
    plot_on_ra_dec(
        axs[1, 1],
        RAcorn,
        DECcorn,
        lexi_bgnd_corrected,
        "lexi_bgnd_corrected",
        vmin=vmin_lexi,
        vmax=vmax_lexi,
    )

    axs[0, 0].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="k", linewidths=0.6, alpha=0.5
    )
    axs[0, 0].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="w", linewidths=0.6, alpha=0.5
    )
    axs[0, 1].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="k", linewidths=0.6, alpha=0.5
    )
    axs[0, 1].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="w", linewidths=0.6, alpha=0.5
    )
    axs[1, 0].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="k", linewidths=0.6, alpha=0.5
    )
    axs[1, 0].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="w", linewidths=0.6, alpha=0.5
    )
    axs[1, 1].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="k", linewidths=0.6, alpha=0.5
    )
    axs[1, 1].contour(
        RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="w", linewidths=0.6, alpha=0.5
    )

    # plt.tight_layout()
    figure_path = Path(f"../figures/exposure_maps/bg_corrected/{delta_time_minutes}min/")
    figure_path.mkdir(parents=True, exist_ok=True)
    fig_name = (
        input_params["time_range"][0].replace(" ", "_").replace(":", "")
        + "_to_"
        + input_params["time_range"][1].replace(" ", "_").replace(":", "")
        + "_exposure_maps.png"
    )
    fig.savefig(figure_path / fig_name, dpi=150)
    # plt.show()
    plt.close()

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
