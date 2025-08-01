import glob
import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from spacepy.pycdf import CDF as cdf

# Define the folder containing the CDF files
folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf/2025-03-16/"

# Get the list of CDF files in the folder and subfolders
file_val_list = sorted(glob.glob(str(folder_name) + "/**/*V0.3.cdf", recursive=True))

read_files = True
df_list = []
if read_files:

    selected_columns = [
        "Epoch",
        "photon_x_mcp",
        "photon_y_mcp",
        "photon_RA",
        "photon_Dec",
        "photon_az",
        "photon_el",
    ]
    for file_val in file_val_list:
        print(f"Reading file: {file_val} of {len(file_val_list)}")
        dat = cdf(file_val)
        dft = pd.DataFrame({key: dat[key][:] for key in selected_columns})
        # Convert the CDF data to a DataFrame
        df_list.append(dft)
    # Concatenate all DataFrames into a single DataFrame
    df = pd.concat(df_list, ignore_index=True)
    # Convert the Epoch column to datetime
    df["Epoch"] = pd.to_datetime(df["Epoch"], unit="s", utc=True)
    # Set the Epoch column as the index
    df.set_index("Epoch", inplace=True)

# Resample to 1-second intervals and count the number of data points
df["Epoch"] = df.index
df["Epoch_seconds"] = df["Epoch"].dt.ceil("S")
counts_per_second = df.groupby("Epoch_seconds").size()
# Save the counts to a CSV file
output_csv_file = Path("../data/counts_per_second.csv")
output_csv_file.parent.mkdir(parents=True, exist_ok=True)
counts_per_second.to_csv(output_csv_file)


fig, axs = plt.subplots(3, 1, figsize=(12, 10))
axs[0].set_aspect("equal")  # Set equal aspect ratio for MCP coordinates plot
axs[0].hist2d(df["photon_x_mcp"], df["photon_y_mcp"], bins=50, cmap="Blues")
axs[0].set_title("X vs Y (Detector Coordinates)")
axs[0].set_xlabel("X (Detector)")
axs[0].set_ylabel("Y (Detector)")
# Add the color bar to the first subplot
cbar = plt.colorbar(axs[0].collections[0], ax=axs[0], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")

axs[1].set_aspect("equal")  # Set equal aspect ratio for RA vs Dec plot
axs[1].hist2d(df["photon_RA"], df["photon_Dec"], bins=50, cmap="Reds")
axs[1].set_title("RA vs Dec")
axs[1].set_xlabel("RA (Degrees)")
axs[1].set_ylabel("Dec (Degrees)")
# Add the color bar to the second subplot
cbar = plt.colorbar(axs[1].collections[0], ax=axs[1], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")

"""
axs[1, 0].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[1, 0].hist2d(
    df["photon_x_lunar"], df["photon_y_lunar"], bins=50, cmap="Greens"
)
axs[1, 0].set_title("Photon X vs Y (Lunar Coordinates)")
axs[1, 0].set_xlabel("Photon X (Lunar)")
axs[1, 0].set_ylabel("Photon Y (Lunar)")
# Add the color bar to the third subplot
cbar = plt.colorbar(axs[1, 0].collections[0], ax=axs[1, 0])
cbar.set_label("Counts")

axs[1, 1].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[1, 1].hist2d(
    df["photon_y_lunar"], df["photon_z_lunar"], bins=50, cmap="Purples"
)
axs[1, 1].set_title("Photon Y vs Z (Lunar Coordinates)")
axs[1, 1].set_xlabel("Photon Y (Lunar)")
axs[1, 1].set_ylabel("Photon Z (Lunar)")
# Add the color bar to the fourth subplot
cbar = plt.colorbar(axs[1, 1].collections[0], ax=axs[1, 1])
cbar.set_label("Counts")

axs[2, 0].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[2, 0].hist2d(
    df["photon_z_lunar"], df["photon_x_lunar"], bins=50, cmap="Oranges"
)
axs[2, 0].set_title("Photon Z vs X (Lunar Coordinates)")
axs[2, 0].set_xlabel("Photon Z (Lunar)")
axs[2, 0].set_ylabel("Photon X (Lunar)")
# Add the color bar to the fifth subplot
cbar = plt.colorbar(axs[2, 0].collections[0], ax=axs[2, 0])
cbar.set_label("Counts")
"""
axs[2].set_aspect("equal")  # Set equal aspect ratio for Lunar coordinates plot
axs[2].hist2d(df["photon_az"], df["photon_el"], bins=50, cmap="Purples")
axs[2].set_title("Az vs El (Lunar Coordinates)")
axs[2].set_xlabel("Azimuth (Degrees)")
axs[2].set_ylabel("Elevation (Degrees)")
# Add the color bar to the sixth subplot
cbar = plt.colorbar(axs[2].collections[0], ax=axs[2], orientation="vertical", shrink=0.8, pad=0.01)
cbar.set_label("Counts")
# axs[2, 1].set_aspect("auto")  # Set equal aspect ratio for Lunar coordinates plot
# axs[2, 1].hist2d(
#     df["photon_z_lunar"], df["photon_xy_lunar"], bins=50, cmap="Greys"
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
    fig_folder / "photon_coordinates_histograms_from_l1c.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.1,
)
code_end_time = time.time()
