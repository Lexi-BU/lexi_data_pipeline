import glob
import importlib
from pathlib import Path

import get_l1c_files_sci_parallel as gl1c
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser
from spacepy.pycdf import CDF as cdf

gl1c = importlib.reload(gl1c)
folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1b/sci/cdf/2025-03-16/"
file_val_list = sorted(glob.glob(str(folder_name) + "/**/*.cdf", recursive=True))

start_time = "2025-03-16T19:00:00Z"
end_time = "2025-03-16T19:59:59Z"
start_time = parser.parse(start_time)
end_time = parser.parse(end_time)

dat = cdf(file_val_list[1])
selected_columns = ["Epoch", "x_mcp", "y_mcp"]
df = pd.DataFrame({key: dat[key][:] for key in selected_columns})

df.rename(columns={"x_mcp": "photon_x_mcp", "y_mcp": "photon_y_mcp"}, inplace=True)
df["photon_z_mcp"] = 37.5  # This is the focal

# Drop all the rows where the photon_x_mcp or photon_y_mcp is NaN
df.dropna(subset=["photon_x_mcp", "photon_y_mcp"], inplace=True)

# Exclude all the rows where the photon_x_mcp or photon_y_mcp is either less than -5.5 or greater than 5.5
df = df[(df["photon_x_mcp"] >= -5.5) & (df["photon_y_mcp"] >= -5.5)]
df = df[(df["photon_x_mcp"] <= 5.5) & (df["photon_y_mcp"] <= 5.5)]
n_points = len(df)
processed_df = gl1c.level1c_data_processing_parallel(df.head(n_points))

# Make a 2 by 2 plot of histogram between:
# 1. photon_x_mcp and photon_y_mcp
# 2. photon_RA and photon_Dec
# 3. photon_x_lunar and photon_y_lunar

fig, axs = plt.subplots(2, 2, figsize=(12, 10))
axs[0, 0].set_aspect("equal")  # Set equal aspect ratio for MCP coordinates plot
axs[0, 0].hist2d(processed_df["photon_x_mcp"], processed_df["photon_y_mcp"], bins=50, cmap="Blues")
axs[0, 0].set_title("Photon X vs Y (MCP Coordinates)")
axs[0, 0].set_xlabel("Photon X (MCP)")
axs[0, 0].set_ylabel("Photon Y (MCP)")
# Add the color bar to the first subplot
cbar = plt.colorbar(axs[0, 0].collections[0], ax=axs[0, 0])
cbar.set_label("Counts")

axs[0, 1].set_aspect("auto")  # Set equal aspect ratio for RA vs Dec plot
axs[0, 1].hist2d(processed_df["photon_RA"], processed_df["photon_Dec"], bins=50, cmap="Reds")
axs[0, 1].set_title("Photon RA vs Dec")
axs[0, 1].set_xlabel("Photon RA (Degrees)")
axs[0, 1].set_ylabel("Photon Dec (Degrees)")
# Add the color bar to the second subplot
cbar = plt.colorbar(axs[0, 1].collections[0], ax=axs[0, 1])
cbar.set_label("Counts")

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

axs[1, 1].axis("off")  # Hide the empty subplot

plt.tight_layout()

fig_folder = Path("../figures/")
fig_folder.mkdir(parents=True, exist_ok=True)
plt.savefig(
    fig_folder / f"photon_coordinates_histograms_{n_points}_points.png",
    dpi=300,
    bbox_inches="tight",
    pad_inches=0.1,
)
