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
import save_data_to_cdf_l1c as sdtc
from dateutil import parser
from spacepy.pycdf import CDF as cdf
from tqdm import tqdm  # Import tqdm for the progress bar

importlib.reload(sdtc)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


# Precompute transformation matrices
deg2rad = np.pi / 180


def get_rotation_matrix():
    Rdb = np.array(
        [
            [np.cos((180 - 55.36) * deg2rad), np.cos(38.17 * deg2rad), np.cos(75.96 * deg2rad)],
            [np.cos((180 - 76.31) * deg2rad), np.cos(116.02 * deg2rad), np.cos(29.89 * deg2rad)],
            [np.cos((180 - 142.0) * deg2rad), np.cos(64.19 * deg2rad), np.cos(64.19 * deg2rad)],
        ]
    )
    Rbd = Rdb.T

    Rlb = np.array(
        [
            [np.cos((180 - 55.36) * deg2rad), np.cos(38.17 * deg2rad), np.cos(75.96 * deg2rad)],
            [np.cos((180 - 76.31) * deg2rad), np.cos(116.02 * deg2rad), np.cos(29.89 * deg2rad)],
            [np.cos((180 - 142.0) * deg2rad), np.cos(64.19 * deg2rad), np.cos(64.19 * deg2rad)],
        ]
    )
    Rbl = Rlb.T

    return Rbd, Rbl


Rbd, Rbl = get_rotation_matrix()


def transform_points(X, R):
    return X @ R.T  # X: (N, 3), R.T: (3, 3)


def compute_ra_dec(X):
    r = np.linalg.norm(X, axis=1)
    RA = np.degrees(np.arctan2(X[:, 1], X[:, 0]))
    Dec = np.degrees(np.arcsin(X[:, 2] / r))
    return RA, Dec


def level1c_data_processing(df):
    X_mcp = df[["photon_x_mcp", "photon_y_mcp", "photon_z_mcp"]].to_numpy()
    X_lander = transform_points(X_mcp, Rbd)
    X_lunar = transform_points(X_lander, Rbl)
    RA, Dec = compute_ra_dec(X_lander)

    df["photon_x_lander"], df["photon_y_lander"], df["photon_z_lander"] = X_lander.T
    df["photon_x_lunar"], df["photon_y_lunar"], df["photon_z_lunar"] = X_lunar.T
    df["photon_RA"] = RA
    df["photon_Dec"] = Dec

    return df[
        [
            "Epoch",
            "photon_x_mcp",
            "photon_y_mcp",
            "photon_x_lunar",
            "photon_y_lunar",
            "photon_z_lunar",
            "photon_RA",
            "photon_Dec",
        ]
    ]


def process_file_group(hour_bin, files, start_time, output_sci_folder):
    """
    Function to process a group of files in parallel

    Parameters
    ----------
    hour_bin : str
        Hour bin for the files.
    files : list
        List of file paths to process.
    start_time : datetime.datetime
        Start time for the processing.
    output_sci_folder : str
        Output folder for the processed data.
    """

    bin_start_time = start_time + datetime.timedelta(hours=hour_bin)
    bin_end_time = bin_start_time + datetime.timedelta(hours=1)

    selected_columns = ["Epoch", "x_mcp", "y_mcp"]

    all_data = []
    for file, file_time in files:
        dat = cdf(file)
        # For all keys, convert the data to a DataFrame for selected columns
        df = pd.DataFrame({key: dat[key][:] for key in selected_columns})
        all_data.append(df)

    # Concatenate all DataFrames
    combined_df = pd.concat(all_data, ignore_index=True)

    # Rename the "x_mcp" to "photon_x_mcp" and "y_mcp" to "photon_y_mcp"
    combined_df.rename(columns={"x_mcp": "photon_x_mcp", "y_mcp": "photon_y_mcp"}, inplace=True)
    # Add a column for the z_mcp coordinate, which is set to 0
    combined_df["photon_z_mcp"] = 0.0

    # print(combined_df.head())
    # Apply the Level 1C data processing
    processed_df = level1c_data_processing(combined_df)

    # Get the date and time for the filename
    bin_start_time_str = bin_start_time.strftime("%Y-%m-%d")

    # Correct file path
    output_sci_file_name = (
        output_sci_folder
        / bin_start_time_str
        / f"payload_lexi_{bin_start_time.strftime('%Y-%m-%d_%H-%M-%S')}_to_{bin_end_time.strftime('%Y-%m-%d_%H-%M-%S')}_sci_output_L1c_v0.0.cdf"
    )

    print(f"saved file: {output_sci_file_name}")

    # Check if the file by that version number already exists, if it does, then increase the version
    # number by 1 and save the file with that version number
    primary_version = 0
    secondary_version = 0
    while True:
        # Check if the file exists
        if output_sci_file_name.exists():
            # If it exists, increase the version number
            secondary_version += 1
            output_sci_file_name = (
                output_sci_file_name.parent
                / f"{output_sci_file_name.stem}_v{primary_version}.{secondary_version}.cdf"
            )
        else:
            break
        # Increment secondary version; if it exceeds 9, increment primary version and reset secondary
        if secondary_version > 9:
            primary_version += 1
            secondary_version = 0

    # Based on the secondary version, create the folder if it doesn't exist
    output_sci_file_name.parent.mkdir(parents=True, exist_ok=True)

    # Set the index to the "Epoch" column
    processed_df.set_index("Epoch", inplace=True)
    # Convert the index to datetime
    processed_df.index = pd.to_datetime(processed_df.index, unit="s", utc=True)
    # Convert the index to a timezone-aware datetime
    processed_df.index = processed_df.index.tz_convert("UTC")

    print(processed_df.keys())
    # Save the processed DataFrame to the output file
    sdtc.save_data_to_cdf(
        df=processed_df,
        file_name=output_sci_file_name,
        file_version=f"{primary_version}.{secondary_version}",
    )


def main(start_time=None, end_time=None):
    # Get the list of files in the folder and subfolders
    sci_folder = "/mnt/cephadrius/bu_research/lexi_data/L1b/sci/cdf/"

    # Get all files in the folder and subfolders
    file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.cdf", recursive=True))

    print(f"Found {len(file_val_list)} files in {sci_folder}")

    # Filter files based on the start and end time
    if start_time is not None and end_time is not None:
        start_time = parser.parse(start_time)
        end_time = parser.parse(end_time)
        file_val_list = [
            file
            for file in file_val_list
            if (
                (match := re.search(r"payload_lexi_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", file))
                and start_time
                <= datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S").replace(
                    tzinfo=datetime.timezone.utc
                )
                <= end_time
            )
        ]
    else:
        # Select all files
        file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.cdf", recursive=True))

    # Define reference start time
    start_time = datetime.datetime(2025, 1, 16, 0, 0, 0, tzinfo=datetime.timezone.utc)
    # Dictionary to store grouped files
    grouped_files = defaultdict(list)
    # Extract timestamps from filenames and group by 1-hour periods
    for file in file_val_list:
        (match := re.search(r"payload_lexi_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", file))

        if match:
            file_time = datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S").replace(
                tzinfo=datetime.timezone.utc
            )

            # Compute the hour bin index
            delta = file_time - start_time
            hour_bin = delta.total_seconds() // 3600

            # Assign to the corresponding group (fix incorrect append)
            grouped_files[hour_bin].append((file, file_time))
    # Convert groups to a sorted list
    sorted_groups = {k: sorted(v, key=lambda x: x[1]) for k, v in sorted(grouped_files.items())}
    # Output folder for merged files
    output_sci_folder = Path("/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf/")
    output_sci_folder.mkdir(parents=True, exist_ok=True)

    # Use ProcessPoolExecutor to parallelize the processing of file groups
    with ProcessPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = {
            executor.submit(
                process_file_group, hour_bin, files, start_time, output_sci_folder
            ): hour_bin
            for hour_bin, files in sorted_groups.items()
        }

        # Use tqdm to display a progress bar
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing file groups"
        ):
            hour_bin = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing hour bin {hour_bin}: {e}")


start_date = 16
start_hour = 18
end_hour = 22

time_of_code = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if __name__ == "__main__":
    for month in range(3, 4):
        for day in range(start_date, start_date + 2):
            for hour in range(start_hour, end_hour):
                start_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:00:00Z"
                end_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:59:59Z"
                print(f"Processing from {start_time} to {end_time}")
                main(start_time=start_time, end_time=end_time)
    print(f"\n\nProcessing completed for {start_date} from {start_hour} to {end_hour}")
