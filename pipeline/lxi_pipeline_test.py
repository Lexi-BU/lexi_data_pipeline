import datetime
import glob
import importlib
from pathlib import Path

import lxi_pipeline_file as lpf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

importlib.reload(lpf)

# Activate the latex text rendering
plt.rc("text", usetex=True)
plt.rc("font", family="serif")

folder_val = "../data/from_LEXI/surface/"
folder_val = Path(folder_val).expanduser().resolve()

multiple_files = False
t_start = "2025-03-02 00:00:00"
t_end = "2026-03-04 00:12:00"

# Compute t_start and t_end in unix time
dt_start = datetime.datetime.strptime(t_start, "%Y-%m-%d %H:%M:%S")
dt_end = datetime.datetime.strptime(t_end, "%Y-%m-%d %H:%M:%S")

t_start_unix = dt_start.replace(tzinfo=datetime.timezone.utc).timestamp()
t_end_unix = dt_end.replace(tzinfo=datetime.timezone.utc).timestamp()

# Get the file name
folder_val_str = str(folder_val)
# Get all files in the folder and subfolders
file_val_list = glob.glob(folder_val_str + "/**/*.dat", recursive=True)

# Selecct the files that are within the time range
file_val_list = [
    file_val
    for file_val in file_val_list
    if (int(file_val.split("/")[-1].split("_")[2]) >= t_start_unix)
    and (int(file_val.split("/")[-1].split("_")[2]) <= t_end_unix)
]
"""
df_sci_l1c_list = []
for i, file_val in enumerate(file_val_list[::5]):
    file_name, df_sci, df_sci_l1b, df_sci_l1c, df_eph = lpf.read_binary_file(
        file_val=file_val, t_start=t_start, t_end=t_end, multiple_files=multiple_files
    )
    # Print in bold red color the file number and the file name
    print(f"\033[1;31;40mFile number {i}\033[0m")
    # If file_name is None, then skip to the next file
    if file_name is None:
        continue
    # Add the data frame to the list
    df_sci_l1c_list.append(df_sci_l1c)

# Concatenate the data frames
df_sci_l1c_all = pd.concat(df_sci_l1c_list)

# Select every 100th row
df_sci_l1c_new = df_sci_l1c_all.iloc[::100]
"""
# Make a time series plot of RA, dec
fig, ax = plt.subplots(2, 1, figsize=(8, 8))
ax[0].scatter(
    df_sci_l1c_new.index,
    df_sci_l1c_new["ra_J2000_deg"],
    label="RA",
    s=0.1,
    c="r",
    marker=".",
    alpha=0.5,
)
ax[0].set_xlabel("Time")
ax[0].set_ylabel("RA [deg]")
ax[0].set_ylim(0, 360)
ax[0].grid()
# Set the y-axis limits
ax[0].set_ylim(200, 330)

ax[1].scatter(
    df_sci_l1c_new.index,
    df_sci_l1c_new["dec_J2000_deg"],
    label="dec",
    s=0.1,
    c="b",
    marker=".",
    alpha=0.5,
)
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Dec [deg]")
ax[1].set_ylim(-90, 90)
ax[1].grid()
ax[1].set_ylim(-30, -10)

file_date = file_name.split("/")[-1].split("_")[2]

folder_fig = Path("../figures")
folder_fig.mkdir(parents=True, exist_ok=True)
# Save the figure
fig.savefig(f"../figures/RA_dec_{file_date}.png", dpi=300, bbox_inches="tight")


# Make a plot of RA vs dec
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.scatter(
    df_sci_l1c_new["ra_J2000_deg"],
    df_sci_l1c_new["dec_J2000_deg"],
    label="RA vs dec",
    s=0.1,
    c="b",
    marker=".",
    alpha=0.5,
)
ax.set_xlabel("RA [deg]")
ax.set_ylabel("Dec [deg]")
ax.set_xlim(200, 260)
ax.set_ylim(-40, 0)

# Save the figure
fig.savefig(f"../figures/RA_vs_dec_{file_date}.png", dpi=300, bbox_inches="tight")

# Make a 2D histogram of RA vs dec
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.hist2d(
    df_sci_l1c_all["ra_J2000_deg"],
    df_sci_l1c_all["dec_J2000_deg"],
    bins=100,
    cmap="viridis",
)
ax.set_xlabel("RA [deg]")
ax.set_ylabel("Dec [deg]")
ax.set_xlim(200, 260)
ax.set_ylim(-40, 0)
fig.colorbar(ax.collections[0], ax=ax, label="Counts")  # Add a colorbar

# Save the figure
fig.savefig(f"../figures/RA_vs_dec_hist_{file_date}.png", dpi=300, bbox_inches="tight")
