import datetime
import glob
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


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
sci_folder = "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/L1a/sci/"

# Get all files in the folder and subfolders
file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.csv", recursive=True))

# Randomly select 100 files for testing
np.random.seed(43)
selected_file_val_list = np.random.choice(file_val_list, size=1, replace=False)

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
output_sci_folder = Path("/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/L1b/sci/")
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
    date_str = bin_start_time.strftime("%Y-%m-%d_%H-%M-%S")
    output_file = output_sci_folder / f"merged_{date_str}.csv"

    # Save to CSV
    processed_df.to_csv(output_file, index=False)
    print(f"Saved merged file for {bin_start_time} to {output_file}")
    output_file = output_sci_folder / f"merged_{date_str}.csv"
