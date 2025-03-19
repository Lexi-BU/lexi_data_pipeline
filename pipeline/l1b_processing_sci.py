import pickle
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def lin_correction(
    x,
    y,
    M_inv=np.array([[0.98678, 0.16204], [0.11385, 0.993497]]),
    b=np.array([0.5568, 0.5600]),
):
    """
    Function to apply linearity correction to MCP position x/y data
    """
    x_lin = (x * M_inv[0, 0] + y * M_inv[0, 1]) - b[0]
    y_lin = x * M_inv[1, 0] + y * M_inv[1, 1] - b[1]

    return x_lin, y_lin


def volt_to_mcp(x, y):
    """
    Function to convert voltage coordinates to MCP coordinates
    """
    conversion_factor = 90
    x_mcp = x * conversion_factor
    y_mcp = y * conversion_factor

    return x_mcp, y_mcp


def non_lin_correction(
    x,
    y,
):
    """
    Function to apply nonlinearity correction to MCP position x/y data. The model to apply the
    nonlinearity correction is a Gaussian Process model trained on the data from the LEXI massk
    testing. The kernel used is Matern with length scale = 5 and nu = 2.5.

    Parameters
    ----------
    x : numpy.ndarray
        x position data.
    y : numpy.ndarray
        y position data.

    Returns
    -------
    x_nln : numpy.ndarray
        x position data after applying nonlinearity correction.
    y_nln : numpy.ndarray
        y position data after applying nonlinearity correction.
    """
    # gp_model_file_name = (
    #     "../data/gp_models/gp_data_3.0_10_0.0_0.8_4_Matern(length_scale=5, nu=2.5).pickle"
    # )
    gp_model_file_name = "../data/gp_models/gp_data_3.0_10_0.0_0.8_4_RationalQuadratic(alpha=0.5, length_scale=5).pickle"

    # Get the gp_model from the pickle file
    with open(gp_model_file_name, "rb") as f:
        gp_model = pickle.load(f)

    # Close the pickle file
    f.close()

    xy_coord = np.array([x, y]).T
    delta_xy, sigma = gp_model.predict(xy_coord, return_std=True)

    corrected_xy = xy_coord - delta_xy
    x_nln = corrected_xy[:, 0]
    y_nln = corrected_xy[:, 1]

    return x_nln, y_nln


def level1b_data_processing(df=None, lower_threshold=None):
    # channel_1_lower_threshold = min(2, df["Channel1"].min())
    # channel_2_lower_threshold = min(2, df["Channel2"].min())
    # channel_3_lower_threshold = min(2, df["Channel3"].min())
    # channel_4_lower_threshold = min(2, df["Channel4"].min())
    if lower_threshold is None:
        channel_1_lower_threshold = 1
        channel_2_lower_threshold = 1
        channel_3_lower_threshold = 1
        channel_4_lower_threshold = 1
    else:
        channel_1_lower_threshold = lower_threshold
        channel_2_lower_threshold = lower_threshold
        channel_3_lower_threshold = lower_threshold
        channel_4_lower_threshold = lower_threshold

    # Compute the shifted values for each channel (only if IsCommanded is False), otherwise set to
    # NaN
    df.loc[df["IsCommanded"] == False, "Channel1_shifted"] = (
        df["Channel1"] - channel_1_lower_threshold
    )
    df.loc[df["IsCommanded"], "Channel1_shifted"] = np.nan
    df.loc[df["Channel1_shifted"] < 0, "Channel1_shifted"] = np.nan

    df.loc[df["IsCommanded"] == False, "Channel2_shifted"] = (
        df["Channel2"] - channel_2_lower_threshold
    )
    df.loc[df["IsCommanded"], "Channel2_shifted"] = np.nan
    df.loc[df["Channel2_shifted"] < 0, "Channel2_shifted"] = np.nan

    df.loc[df["IsCommanded"] == False, "Channel3_shifted"] = (
        df["Channel3"] - channel_3_lower_threshold
    )
    df.loc[df["IsCommanded"], "Channel3_shifted"] = np.nan
    df.loc[df["Channel3_shifted"] < 0, "Channel3_shifted"] = np.nan

    df.loc[df["IsCommanded"] == False, "Channel4_shifted"] = (
        df["Channel4"] - channel_4_lower_threshold
    )
    df.loc[df["IsCommanded"], "Channel4_shifted"] = np.nan
    df.loc[df["Channel4_shifted"] < 0, "Channel4_shifted"] = np.nan

    # Compute the position in voltage coordiantes
    df["x_volt"] = df["Channel3_shifted"] / (df["Channel3_shifted"] + df["Channel1_shifted"])
    df["y_volt"] = df["Channel2_shifted"] / (df["Channel2_shifted"] + df["Channel4_shifted"])

    # Apply the linear correction
    df["x_volt_lin"], df["y_volt_lin"] = lin_correction(df["x_volt"], df["y_volt"])
    # Apply the voltage to MCP conversion
    df["x_mcp"], df["y_mcp"] = volt_to_mcp(df["x_volt_lin"], df["y_volt_lin"])

    # Apply the nonlinearity correction
    df["x_mcp_nln"], df["y_mcp_nln"] = non_lin_correction(df["x_mcp"], df["y_mcp"])

    return df


def make_thresholded_histogram(
    df=None,
    lower_threshold=1.3,
    upper_threshold=3.3,
    sum_lower_threshold=8,
    sum_upper_threshold=12,
    histogram_x_key="x_cm",
    histogram_y_key="y_cm",
    bins=100,
    min_count=1,
    holes_data=None,
    save_fig=False,
    fig_name=None,
    file_name=None,
):

    # Remove all the rows where the Channel1 value is less than the lower threshold value and greater
    # than the upper threshold value
    df = df[(df["Channel1"] >= lower_threshold) & (df["Channel1"] <= upper_threshold)]
    df = df[(df["Channel2"] >= lower_threshold) & (df["Channel2"] <= upper_threshold)]
    df = df[(df["Channel3"] >= lower_threshold) & (df["Channel3"] <= upper_threshold)]
    df = df[(df["Channel4"] >= lower_threshold) & (df["Channel4"] <= upper_threshold)]

    # Compute the sum of the Channel1, Channel2, Channel3, and Channel4 values
    df["Sum"] = df["Channel1"] + df["Channel2"] + df["Channel3"] + df["Channel4"]

    # Remove all the rows where the sum value is less than the sum lower threshold value and greater
    # than the sum upper threshold value
    df = df[(df["Sum"] >= sum_lower_threshold) & (df["Sum"] <= sum_upper_threshold)]

    delta_x = 0  # .48000
    delta_y = 0  # .50853
    df[histogram_x_key] = df[histogram_x_key] - delta_x  # * 136 / 6
    df[histogram_y_key] = df[histogram_y_key] - delta_y  # * 152 / 6
    # Use white background
    plt.style.use("default")

    # Create a 2d histogram using numpy
    hist, xedges, yedges = np.histogram2d(
        df[histogram_x_key], df[histogram_y_key], bins=bins, range=[[-0.5, 0.5], [-0.5, 0.5]]
    )
    # Save the histogram data to a pickle file
    histogram_data = {
        "hist": hist,
        "xedges": xedges,
        "yedges": yedges,
    }
    histogram_file_name = f"{file_name.split('/')[-1].split('.')[0]}_histogram_{histogram_x_key}_vs_{histogram_y_key}.pickle"
    histogram_file_path = Path("../data/histograms/")
    histogram_file_path.mkdir(parents=True, exist_ok=True)
    with open(histogram_file_path / histogram_file_name, "wb") as f:
        pickle.dump(histogram_data, f)
    f.close()
    # Create a hexbin 2d histogram plot
    fig, ax = plt.subplots(figsize=(8, 6))
    hb = ax.hexbin(
        df[histogram_x_key],
        df[histogram_y_key],
        gridsize=bins,
        cmap="bone_r",
        mincnt=min_count,
        norm=mpl.colors.LogNorm(vmin=min_count, vmax=min_count + 2),
        edgecolors="none",
    )

    ax.set_xlabel(histogram_x_key)
    ax.set_ylabel(histogram_y_key)
    ax.set_facecolor("white")
    ax.set_aspect("equal", adjustable="box")
    if "volt_lin" in histogram_x_key:
        ax.set_xlim(-0.05, 0.05)
        ax.set_ylim(-0.05, 0.05)
    elif "volt" in histogram_x_key:
        ax.set_xlim(0.42, 0.56)
        ax.set_ylim(0.44, 0.58)
    elif "cm" in histogram_x_key:
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4.5, 4.5)
    elif "mcp" in histogram_x_key:
        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4.5, 4.5)
    # ax.set_xlim(0.400 - delta_x, 0.550 - delta_x)
    # ax.set_ylim(0.450 - delta_y, 0.600 - delta_y)
    # Set the title of the plot to the file name
    if file_name is not None:
        title = file_name.split("/")[-1].split(".")[0]
        ax.set_title(title, fontsize=10)
    else:
        ax.set_title("Thresholded Histogram")
    # Add grid lines
    ax.grid(True, linestyle="--", alpha=0.5, color="gray")
    # Add a colorbar
    cb = plt.colorbar(hb)
    cb.set_label("Counts")

    # Plot a vertical line at x = 0 and y = 0
    # ax.axvline(x=0, color="b", lw=1)
    # ax.axhline(y=0, color="r", lw=1)
    # Plot a line at -10 degrees with respect to the x-axis
    # theta = -6
    # theta_rad = np.radians(theta)
    # slope = np.tan(theta_rad)
    # x_vals = np.linspace(-0.5, 0.5, 100)
    # y_vals = slope * x_vals
    # ax.plot(x_vals, y_vals, color="orange", lw=1)
    # # Plot a line at 10 degrees with respect to the x-axis
    # theta = 99
    # theta_rad = np.radians(theta)
    # slope = np.tan(theta_rad)
    # y_vals = slope * x_vals
    # ax.plot(x_vals, y_vals, color="m", lw=1)

    # Set the title of the plot to the file name
    if file_name is not None:
        title = file_name.split("/")[-1].split(".")[0]
        ax.set_title(title, fontsize=10)
    else:
        ax.set_title("Thresholded Histogram")
    # If holes data is provided, plot the holes
    if holes_data is not None:
        ax.scatter(holes_data[0], holes_data[1], label="Holes", color="red", s=10, alpha=0.5)
        plt.legend()

    if save_fig:
        if fig_name is None:
            fig_name = f"thresholded_histogram_{histogram_x_key}_vs_{histogram_y_key}.png"
        # Save the figure
        fig_folder = Path("../figures/nlin_correction/")
        fig_folder.mkdir(parents=True, exist_ok=True)
        print(f"Saving figure to {fig_folder / fig_name}")
        plt.savefig(fig_folder / fig_name, dpi=300, bbox_inches="tight")
    # plt.show()
    # Close the figure
    # plt.close(fig)
    return fig, ax
