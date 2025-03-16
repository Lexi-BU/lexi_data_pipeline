import glob
from pathlib import Path

from spacepy.pycdf import CDF as cdf

folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1b/sci/cdf/2025-01-16"

# Get all files in the folder and subfolders
file_val_list = sorted(glob.glob(str(folder_name) + "/*.cdf", recursive=True))

for file_val in file_val_list[0:]:
    try:
        dat = cdf(file_val)
        # Get the start and end time of the file
        start_time = dat["Epoch"][0]
        end_time = dat["Epoch"][-1]
        # Get all the variables in the file
        variables = dat.keys()
        print(f"Start time: {start_time}, End time: {end_time}, Duration: {end_time - start_time}")
    except Exception:
        # print(f"Error reading file {file_val}: {e}")
        continue
