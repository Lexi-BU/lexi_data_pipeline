import datetime
import glob
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from spacepy.pycdf import CDF as cdf

# l2_files = sorted(glob.glob("/mnt/cephadrius/bu_research/lexi_data/l2/*.cdf"))
l2_files = sorted(glob.glob("/home/vetinari/Desktop/git/Lexi-Bu/lexi_data_pipeline/data/l2/*.cdf"))


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


def plot_on_ra_dec(
    ax,
    ra_corners,
    dec_corners,
    data,
    title=None,
    cbar_title=None,
    time_range=None,
    vmin=None,
    vmax=None,
    norm="linear",
):
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
    time_range = pd.to_datetime(time_range, utc=True)
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
    cbar = plt.colorbar(
        pm, ax=ax, label=cbar_title, orientation="vertical", fraction=0.046, pad=0.00
    )

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


warnings.filterwarnings("ignore")
keys_to_plot = [
    "exposure_map",
    "flat_field_map",
    "background_map",
    "lexi_hist",
    "lexi_histogram_bgnd_corrected",
    "lexi_histogram_bgnd_flat_corrected",
]


for i, f in enumerate(l2_files[:]):
    dat = cdf(f)

    print(f"Reading file: {f}, {i + 1} out of {len(l2_files)}", end="\r")
    ra_c = np.asarray(dat["ra_bin_map"][...])[0]
    dec_c = np.asarray(dat["dec_bin_map"][...])[0]
    time_range = [dat["epoch_start"][...][0], dat["epoch_end"][...][0]]
    RAcorn, DECcorn = centers_to_corners_2d(ra_c, dec_c)

    # Plot the exposure maps and counts
    fig, axs = plt.subplots(2, 3, figsize=(20, 12), constrained_layout=True)
    # Set the hspace and wspace
    fig.subplots_adjust(hspace=0.0, wspace=0.0)
    # Set the default font size
    mpl.rcParams.update({"font.size": 16})
    fig.suptitle(f"LEXI L2 Data from {Path(f).name}", fontsize=20)

    plot_on_ra_dec(
        axs[0, 0],
        RAcorn,
        DECcorn,
        np.asarray(dat["exposure_map"][...])[0],
        time_range=time_range,
        title="Exposure Map",
        cbar_title="Exposure Time (s)",
        norm="log",
        vmin=1e0,
        vmax=3e2,
    )
    plot_on_ra_dec(
        axs[0, 1],
        RAcorn,
        DECcorn,
        np.asarray(dat["flat_field_map"][...])[0],
        title="Flat Field Map.)",
        cbar_title="Normalized Counts",
        time_range=time_range,
        vmin=1e-1,
        vmax=1e0,
        norm="log",
    )
    plot_on_ra_dec(
        axs[0, 2],
        RAcorn,
        DECcorn,
        np.asarray(dat["background_map"][...])[0],
        title="Background Map",
        cbar_title="Counts/pixel",
        time_range=time_range,
        norm="log",
        vmin=1e-3,
        vmax=1e-1,
    )
    plot_on_ra_dec(
        axs[1, 0],
        RAcorn,
        DECcorn,
        np.asarray(dat["lexi_hist"][...])[0],
        time_range=time_range,
        title="Raw Counts",
        cbar_title="Counts/sec",
        norm="log",
    )
    plot_on_ra_dec(
        axs[1, 1],
        RAcorn,
        DECcorn,
        np.asarray(dat["lexi_histogram_bgnd_corrected"][...])[0],
        time_range=time_range,
        title="Background-Corrected Counts",
        cbar_title="Counts/sec",
        norm="log",
    )

    plot_on_ra_dec(
        axs[1, 2],
        RAcorn,
        DECcorn,
        np.asarray(dat["lexi_histogram_bgnd_flat_corrected"][...])[0],
        time_range=time_range,
        title="Background & Flat-Field Corrected Counts",
        cbar_title="Counts/sec",
        norm="log",
    )

    for ax in axs.flatten():
        ax.contour(RAcorn[:-1, :-1], DECcorn[:-1, :-1], ra_c, colors="c", linewidths=0.6, alpha=0.5)
        ax.contour(
            RAcorn[:-1, :-1], DECcorn[:-1, :-1], dec_c, colors="k", linewidths=0.6, alpha=0.5
        )
        ax.set_aspect("equal")

    figure_path = Path("../figures/exposure_maps/bg_corrected/from_l2/new/")
    figure_path.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        figure_path / (Path(f).stem + "_exposure_and_counts.png"),
        dpi=200,
        bbox_inches="tight",
        pad_inches=0.1,
    )
    plt.close(fig)
