import datetime
import glob
import importlib
import re
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import save_data_to_cdf as sdtc
from dateutil import parser
from tqdm import tqdm  # Import tqdm for the progress bar

importlib.reload(sdtc)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def lin_correction(
    x,
    y,
    M_inv=np.array([[0.98678, 0.16204], [0.11385, 0.993497]]),
    b=np.array([0.5529, 0.5596]),
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
    # Conversion factor from voltage to MCP coordinates. This is basically the effective diameter
    # over which the MCP is active.

    conversion_factor = 90  # in mm
    x_mcp = x * conversion_factor
    y_mcp = y * conversion_factor

    return x_mcp, y_mcp


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

    return df


def process_file_group(minute_bin, files, start_time, output_sci_folder):
    bin_start_time = start_time + datetime.timedelta(minutes=minute_bin * 5)
    bin_end_time = bin_start_time + datetime.timedelta(minutes=5)

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

    # Correct file path
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


def main(start_time=None, end_time=None):
    # Get the list of files in the folder and subfolders
    sci_folder = "/mnt/cephadrius/bu_research/lexi_data/L1a/sci/csv/"

    # Get all files in the folder and subfolders
    file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.csv", recursive=True))

    # Filter files based on the start and end time
    if start_time is not None and end_time is not None:
        start_time = parser.parse(start_time)
        end_time = parser.parse(end_time)
        # Add a 5 seconds buffer to the start time to include the first minute and 5 seconds buffer to
        # the end time
        # start_time -= datetime.timedelta(seconds=5)
        # end_time += datetime.timedelta(seconds=5)
        file_val_list = [
            file
            for file in file_val_list
            if start_time
            <= datetime.datetime.fromtimestamp(
                int(re.search(r"payload_lexi_(\d+)_", file).group(1)), tz=datetime.timezone.utc
            )
            <= end_time
        ]
    else:
        # Select all files
        file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.csv", recursive=True))

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
            minute_bin = delta.total_seconds() // 300

            # Assign to the corresponding group (fix incorrect append)
            grouped_files[minute_bin].append((file, file_time))
    # Convert groups to a sorted list
    sorted_groups = {k: sorted(v, key=lambda x: x[1]) for k, v in sorted(grouped_files.items())}
    # Output folder for merged files
    output_sci_folder = Path("/mnt/cephadrius/bu_research/lexi_data/L1b/sci/csv/")
    output_sci_folder.mkdir(parents=True, exist_ok=True)

    # Use ProcessPoolExecutor to parallelize the processing of file groups
    with ProcessPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = {
            executor.submit(
                process_file_group, minute_bin, files, start_time, output_sci_folder
            ): minute_bin
            for minute_bin, files in sorted_groups.items()
        }

        # Use tqdm to display a progress bar
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing file groups"
        ):
            minute_bin = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing hour bin {minute_bin}: {e}")


start_date = 9
start_hour = 0
end_hour = 24
start_minute = 0
end_minute = 59
if __name__ == "__main__":
    for month in range(3, 4):
        for day in range(start_date, start_date + 1):
            for hour in range(start_hour, end_hour):
                for minute in range(start_minute, end_minute + 1, 5):
                    start_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00Z"
                    end_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:{minute + 4:02d}:59Z"
                    # print(f"Processing from {start_time} to {end_time}")
                    main(start_time=start_time, end_time=end_time)
    # print(f"\n\nProcessing completed for {start_date} from {start_hour} to {end_hour}")
