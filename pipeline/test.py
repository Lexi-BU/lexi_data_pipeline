import glob
import importlib
import time
from pathlib import Path

import get_l1c_files_sci_parallel as gl1c
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser
from spacepy.pycdf import CDF as cdf

gl1c = importlib.reload(gl1c)
code_start_time = time.time()

folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1b/sci/cdf/2025-03-16/"

file_val_list = sorted(glob.glob(str(folder_name) + "/**/*.cdf", recursive=True))

read_files = True
process_files = True
if read_files:
    dat = cdf(file_val_list[-1])

    selected_columns = ["Epoch", "x_mcp", "y_mcp"]
    all_columns = [
        "Epoch",
        "Epoch_unix",
        "TimeStamp",
        "IsCommanded",
        "Channel1",
        "Channel2",
        "Channel3",
        "Channel4",
        "Channel1_shifted",
        "Channel2_shifted",
        "Channel3_shifted",
        "Channel4_shifted",
        "x_volt",
        "y_volt",
        "x_volt_lin",
        "y_volt_lin",
        "x_mcp",
        "y_mcp",
    ]

    df = pd.DataFrame({key: dat[key][:] for key in all_columns})
    lower_threshold = 2
    upper_threshold = 3.3
    df = df[df["IsCommanded"] == False]
    df = df[
        (df["Channel1"] >= lower_threshold)
        & (df["Channel1"] <= upper_threshold)
        & (df["Channel2"] >= lower_threshold)
        & (df["Channel2"] <= upper_threshold)
        & (df["Channel3"] >= lower_threshold)
        & (df["Channel3"] <= upper_threshold)
        & (df["Channel4"] >= lower_threshold)
        & (df["Channel4"] <= upper_threshold)
    ]
    df = df[selected_columns]

    df.rename(columns={"x_mcp": "photon_x_mcp", "y_mcp": "photon_y_mcp"}, inplace=True)

    df["photon_z_mcp"] = 37.5  # This is the focal

    # Drop all the rows where the photon_x_mcp or photon_y_mcp is NaN
    df.dropna(subset=["photon_x_mcp", "photon_y_mcp"], inplace=True)

    # Exclude all the rows where the absolute value of photon_x_mcp or photon_y_mcp is greater than 5.5
    df = df[(df["photon_x_mcp"].abs() <= 4.5) & (df["photon_y_mcp"].abs() <= 4.5)]
    df["photon_x_mcp"] = df["photon_x_mcp"]
    df["photon_y_mcp"] = df["photon_y_mcp"]
    df["photon_z_mcp"] = df["photon_z_mcp"]


if process_files:
    # Get the every 10th row of the DataFrame
    df_2 = df.iloc[::1000, :].reset_index(drop=True)
    # Sort the DataFrame by the Epoch column
    df_2["Epoch"] = pd.to_datetime(df_2["Epoch"], format="mixed", utc=True)
    df_2.sort_values(by="Epoch", inplace=True)
    # Reset the index of the DataFrame
    df_2.reset_index(drop=True, inplace=True)
    # Set the index of the DataFrame to the Epoch column
    # df_2["Epoch"] = pd.to_datetime(df_2["Epoch"], format="mixed", utc=True)
    # df_2.set_index("Epoch", inplace=True)
    n_points = 1000  # len(df)
    processed_df = gl1c.level1c_data_processing_parallel(df_2.head(n_points))

    #
    # # Save the processed data to a CSV file
    # csv_file = Path(
    #     "../data/payload_lexi_2025-03-16_19-00-00_to_2025-03-16_20-00-00_sci_output_L1c_v0.1.csv"
    # )
    # csv_file.parent.mkdir(parents=True, exist_ok=True)
    # processed_df.to_csv(csv_file, index=False)
    # Make a 2 by 2 plot of histogram between:
    # 1. photon_x_mcp and photon_y_mcp
    # 2. photon_RA and photon_Dec
    # 3. photon_x_lunar and photon_y_lunar

    # processed_df["photon_yz_lunar"] = np.sqrt(
    #     processed_df["photon_y_lunar"] ** 2 + processed_df["photon_z_lunar"] ** 2
    # )
    # processed_df["photon_xy_lunar"] = np.sqrt(
    #     processed_df["photon_x_lunar"] ** 2 + processed_df["photon_y_lunar"] ** 2
    # )
    # processed_df["photon_xz_lunar"] = np.sqrt(
    #     processed_df["photon_x_lunar"] ** 2 + processed_df["photon_z_lunar"] ** 2
    # )

fig, axs = plt.subplots(3, 1, figsize=(12, 10))
axs[0].set_aspect("equal")  # Set equal aspect ratio for MCP coordinates plot
axs[0].hist2d(processed_df["photon_x_mcp"], processed_df["photon_y_mcp"], bins=50, cmap="Blues")
axs[0].set_title("X vs Y (Detector Coordinates)")
axs[0].set_xlabel("X (Detector)")
axs[0].set_ylabel("Y (Detector)")
# Add the color bar to the first subplot
cbar = plt.colorbar(axs[0].collections[0], ax=axs[0], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")

axs[1].set_aspect("equal")  # Set equal aspect ratio for RA vs Dec plot
axs[1].hist2d(processed_df["photon_RA"], processed_df["photon_Dec"], bins=50, cmap="Reds")
axs[1].set_title("RA vs Dec")
axs[1].set_xlabel("RA (Degrees)")
axs[1].set_ylabel("Dec (Degrees)")
# Add the color bar to the second subplot
cbar = plt.colorbar(axs[1].collections[0], ax=axs[1], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")

"""
axs[1, 0].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[1, 0].hist2d(
    processed_df["photon_x_lunar"], processed_df["photon_y_lunar"], bins=50, cmap="Greens"
)
axs[1, 0].set_title("Photon X vs Y (Lunar Coordinates)")
axs[1, 0].set_xlabel("Photon X (Lunar)")
axs[1, 0].set_ylabel("Photon Y (Lunar)")
# Add the color bar to the third subplot
cbar = plt.colorbar(axs[1, 0].collections[0], ax=axs[1, 0])
cbar.set_label("Counts")

axs[1, 1].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[1, 1].hist2d(
    processed_df["photon_y_lunar"], processed_df["photon_z_lunar"], bins=50, cmap="Purples"
)
axs[1, 1].set_title("Photon Y vs Z (Lunar Coordinates)")
axs[1, 1].set_xlabel("Photon Y (Lunar)")
axs[1, 1].set_ylabel("Photon Z (Lunar)")
# Add the color bar to the fourth subplot
cbar = plt.colorbar(axs[1, 1].collections[0], ax=axs[1, 1])
cbar.set_label("Counts")

axs[2, 0].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[2, 0].hist2d(
    processed_df["photon_z_lunar"], processed_df["photon_x_lunar"], bins=50, cmap="Oranges"
)
axs[2, 0].set_title("Photon Z vs X (Lunar Coordinates)")
axs[2, 0].set_xlabel("Photon Z (Lunar)")
axs[2, 0].set_ylabel("Photon X (Lunar)")
# Add the color bar to the fifth subplot
cbar = plt.colorbar(axs[2, 0].collections[0], ax=axs[2, 0])
cbar.set_label("Counts")
"""
axs[2].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[2].hist2d(processed_df["photon_az"], processed_df["photon_el"], bins=50, cmap="Purples")
axs[2].set_title("Az vs El (Lunar Coordinates)")
axs[2].set_xlabel("Azimuth (Degrees)")
axs[2].set_ylabel("Elevation (Degrees)")
# Add the color bar to the sixth subplot
cbar = plt.colorbar(axs[2].collections[0], ax=axs[2], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")
# axs[2, 1].set_aspect("auto")  # Set equal aspect ratio for Lunar coordinates plot
# axs[2, 1].hist2d(
#     processed_df["photon_z_lunar"], processed_df["photon_xy_lunar"], bins=50, cmap="Greys"
# )
# axs[2, 1].set_title("Photon Z vs XY (Lunar Coordinates)")
# axs[2, 1].set_xlabel("Photon Z (Lunar)")
# axs[2, 1].set_ylabel("Photon XY (Lunar)")
# # Add the color bar to the sixth subplot
# cbar = plt.colorbar(axs[2, 1].collections[0], ax=axs[2, 1])
# cbar.set_label("Counts")

plt.tight_layout()

fig_folder = Path("../figures/")
fig_folder.mkdir(parents=True, exist_ok=True)
plt.savefig(
    fig_folder / f"photon_coordinates_histograms_{n_points}_points_mcp_37_detector.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.1,
)
code_end_time = time.time()
print(f"Code execution time: {code_end_time - code_start_time:.3f} seconds")
