import importlib
import glob
import datetime
import numpy as np
from pathlib import Path

# import pandas as pd
import lxi_pipeline_file as lpf
import matplotlib.pyplot as plt

importlib.reload(lpf)

# Activate the latex text rendering
plt.rc("text", usetex=True)
plt.rc("font", family="serif")

folder_val = (
    "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/from_lexi/"
)
multiple_files = False
t_start = "2024-05-23 21:00:00"
t_end = "2024-06-23 22:02:00"

# Compute t_start and t_end in unix time
dt_start = datetime.datetime.strptime(t_start, "%Y-%m-%d %H:%M:%S")
dt_end = datetime.datetime.strptime(t_end, "%Y-%m-%d %H:%M:%S")

t_start_unix = dt_start.replace(tzinfo=datetime.timezone.utc).timestamp()
t_end_unix = dt_end.replace(tzinfo=datetime.timezone.utc).timestamp()

# Get the file name
file_val_list = np.sort(glob.glob(folder_val + "*.dat"))

# Selecct the files that are within the time range
file_val_list = [
    file_val
    for file_val in file_val_list
    if (int(file_val.split("/")[-1].split("_")[2]) >= t_start_unix)
    and (int(file_val.split("/")[-1].split("_")[2]) <= t_end_unix)
]

for file_val in file_val_list[1428:]:
    file_name, df_sci, df_sci_l1b, df_sci_l1c, df_eph = lpf.read_binary_file(
        file_val=file_val, t_start=t_start, t_end=t_end, multiple_files=multiple_files
    )
#     # Make a time series plot of RA, dec
#     fig, ax = plt.subplots(2, 1, figsize=(8, 8))
#     ax[0].scatter(
#         df_sci_l1c.index,
#         df_sci_l1c["ra_J2000_deg"],
#         label="RA",
#         s=0.1,
#         c="r",
#         marker=".",
#         alpha=0.5,
#     )
#     ax[0].set_xlabel("Time")
#     ax[0].set_ylabel("RA [deg]")
#     ax[0].set_ylim(0, 360)
#     ax[0].grid()
# 
#     ax[1].scatter(
#         df_sci_l1c.index,
#         df_sci_l1c["dec_J2000_deg"],
#         label="dec",
#         s=0.1,
#         c="b",
#         marker=".",
#         alpha=0.5,
#     )
#     ax[1].set_xlabel("Time")
#     ax[1].set_ylabel("Dec [deg]")
#     ax[1].set_ylim(-90, 90)
#     ax[1].grid()
# 
#     file_date = file_name.split("/")[-1].split("_")[2]
# 
#     folder_fig = Path("../figures")
#     folder_fig.mkdir(parents=True, exist_ok=True)
#     # Save the figure
#     fig.savefig(f"../figures/RA_dec_{file_date}.png", dpi=300, bbox_inches="tight")
