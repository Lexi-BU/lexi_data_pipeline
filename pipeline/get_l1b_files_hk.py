import datetime
import glob
import importlib
import re
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import save_data_to_cdf as sdtc
from dateutil import parser

importlib.reload(sdtc)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Get the list of files in the folder and subfolders
hk_folder = "/mnt/cephadrius/bu_research/lexi_data/L1a/hk/csv/2025-03-16/"

# Get all files in the folder and subfolders
file_val_list = sorted(glob.glob(str(hk_folder) + "*.csv", recursive=True))

# Randomly select 100 files for testing
np.random.seed(42)
# selected_file_val_list = np.random.choice(file_val_list, size=200, replace=False)

selected_file_val_list = file_val_list[0:]

# Define reference start time
start_time = datetime.datetime(2025, 1, 16, 0, 0, 0, tzinfo=datetime.timezone.utc)

# Dictionary to store grouped files
grouped_files = defaultdict(list)

# Extract timestamps from filenames and group by 1-hour periods
for file in selected_file_val_list:
    match = re.search(r"payload_lexi_(\d+)_", file)
    if match:
        timestamp = int(match.group(1))
        file_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)

        # Compute the hour bin index
        delta = file_time - start_time
        hour_bin = delta.total_seconds() // 3600

        # Assign to the corresponding group (fix incorrect append)
        grouped_files[hour_bin].append((file, file_time))

# Convert groups to a sorted list
sorted_groups = {k: sorted(v, key=lambda x: x[1]) for k, v in sorted(grouped_files.items())}

# Output folder for merged files
output_hk_folder = Path("/mnt/cephadrius/bu_research/lexi_data/L1b/hk/csv/")
output_hk_folder.mkdir(parents=True, exist_ok=True)

# Save each group to a CSV file
for hour_bin, files in sorted_groups.items():
    bin_start_time = start_time + datetime.timedelta(hours=hour_bin)
    bin_end_time = bin_start_time + datetime.timedelta(hours=1)

    all_data = []
    for file, file_time in files:
        df = pd.read_csv(file)
        all_data.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)

    # Backward fill any missing data
    combined_df.ffill(inplace=True)
    # Forward fill any missing data
    combined_df.bfill(inplace=True)

    # Get the date and time for the filename
    bin_start_time_str = bin_start_time.strftime("%Y-%m-%d")
    # Correct file path concatenation
    output_hk_file_name = (
        output_hk_folder
        / bin_start_time_str
        / f"payload_lexi_{bin_start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{bin_end_time.strftime('%Y-%m-%d_%H-%M-%S')}_hk_output_L1b_v0.0.csv"
    )
    # Check if the file by that version number already exists, if it does, then increase the version
    # number by 1 and save the file with that version number
    primary_version = 0
    secondary_version = 0

    while True:
        output_hk_file_name = (
            output_hk_folder
            / bin_start_time_str
            / f"payload_lexi_{bin_start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{bin_end_time.strftime('%Y-%m-%d_%H-%M-%S')}_hk_output_L1b_v{primary_version}.{secondary_version}.csv"
        )

        if not output_hk_file_name.exists():  # Check if file exists
            break  # Stop loop when an unused filename is found

        # Increment secondary version; if it exceeds 9, increment primary version and reset secondary
        secondary_version += 1
        if secondary_version > 9:
            secondary_version = 0
            primary_version += 1

    # Based on the output file name, create the folder if it doesn't exist
    output_hk_file_name.parent.mkdir(parents=True, exist_ok=True)

    # Save merged CSV
    combined_df.to_csv(output_hk_file_name, index=False)
    # print(
    #     f"\n Saved \033[1;94m {Path(output_hk_file_name).parent}/\033[1;92m{Path(output_hk_file_name).name} \033[0m"
    # )

    # Set the Date as index
    combined_df["Date"] = combined_df["Date"].apply(parser.parse)
    try:
        combined_df["Date"] = combined_df["Date"].dt.tz_convert("UTC")
    except Exception:
        combined_df["Date"] = combined_df["Date"].dt.tz_localize("UTC")
    combined_df.set_index("Date", inplace=True)

    # Save the data as cdf file
    sdtc.save_data_to_cdf(
        df=combined_df,
        file_name=output_hk_file_name,
        file_version=f"{primary_version}.{secondary_version}",
    )
    # Print the progress recursively as percentage using \r
    print(
        f"\rProgress: {((hour_bin + 1) / len(selected_file_val_list)) * 100:.5f}%",
        end="",
    )
