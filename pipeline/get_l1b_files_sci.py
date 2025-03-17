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


def level1b_data_processing(df=None):
    channel_1_lower_threshold = min(2, df["Channel1"].min())
    channel_2_lower_threshold = min(2, df["Channel2"].min())
    channel_3_lower_threshold = min(2, df["Channel3"].min())
    channel_4_lower_threshold = min(2, df["Channel4"].min())

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

    detector_size = 6  # The size of MCP detector in cm

    # Compute the position in cm
    df["x_cm"] = (df["x_volt"] - 0.5) * detector_size
    df["y_cm"] = (df["y_volt"] - 0.5) * detector_size

    return df


# Get the list of files in the folder and subfolders
sci_folder = "/mnt/cephadrius/bu_research/lexi_data/L1a/sci/csv/2025-03-16/"

# Get all files in the folder and subfolders
file_val_list = sorted(glob.glob(str(sci_folder) + "*.csv", recursive=True))

# Randomly select 100 files for testing
np.random.seed(43)
# selected_file_val_list = np.random.choice(file_val_list, size=1000, replace=False)

# Define reference start time
start_time = datetime.datetime(2025, 1, 16, 0, 0, 0, tzinfo=datetime.timezone.utc)
# Dictionary to store grouped files
grouped_files = defaultdict(list)
# Extract timestamps from filenames and group by 1-hour periods
for file in file_val_list:
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
output_sci_folder = Path("/mnt/cephadrius/bu_research/lexi_data/L1b/sci/csv/")
output_sci_folder.mkdir(parents=True, exist_ok=True)

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

    # Apply the level1b data processing
    processed_df = level1b_data_processing(combined_df)

    # Get the date and time for the filename
    bin_start_time_str = bin_start_time.strftime("%Y-%m-%d")

    # correct file path
    output_sci_file_name = (
        output_sci_folder
        / bin_start_time_str
        / f"payload_lexi_{bin_start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{bin_end_time.strftime('%Y-%m-%d_%H-%M-%S')}_sci_output_L1b_v0.0.csv"
    )

    # Check if the file by that version number already exists, if it does, then increase the version
    # number by 1 and save the file with that version number
    primary_version = 0
    secondary_version = 0

    while True:
        output_sci_file_name = (
            output_sci_folder
            / bin_start_time_str
            / f"payload_lexi_{bin_start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{bin_end_time.strftime('%Y-%m-%d_%H-%M-%S')}_sci_output_L1b_v{primary_version}.{secondary_version}.csv"
        )

        if not output_sci_file_name.exists():  # Check if file exists
            break  # Stop loop when an unused filename is found

        # Increment secondary version; if it exceeds 9, increment primary version and reset secondary
        secondary_version += 1
        if secondary_version > 9:
            secondary_version = 0
            primary_version += 1

    # Based on the output file name, create the folder if it doesn't exist
    output_sci_file_name.parent.mkdir(parents=True, exist_ok=True)

    # Save merged CSV
    combined_df.to_csv(output_sci_file_name, index=False)
    print(
        f"\n Saved \033[1;94m {Path(output_sci_file_name).parent}/\033[1;92m{Path(output_sci_file_name).name} \033[0m"
    )

    # Set the Date as index
    combined_df["Date"] = combined_df["Date"].apply(parser.parse)
    combined_df["Date"] = combined_df["Date"].dt.tz_convert("UTC")
    # combined_df["Date"] = pd.to_datetime(combined_df["Date"], utc=True)
    # combined_df.set_index("Date", inplace=True)

    # Save the data as cdf file
    sdtc.save_data_to_cdf(
        df=processed_df,
        file_name=output_sci_file_name,
        file_version=f"{primary_version}.{secondary_version}",
    )
