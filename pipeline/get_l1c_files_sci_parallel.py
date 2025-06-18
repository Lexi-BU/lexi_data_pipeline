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
from spacepy.pycdf import CDF as cdf
from tqdm import tqdm  # Import tqdm for the progress bar

importlib.reload(sdtc)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)


def transform_mcp_to_lander(x_mcp, y_mcp, z_mcp):
    """
    Function to transform MCP coordinates to Lander coordinates

    Parameters
    ----------
    x_mcp : float
        X coordinate of the MCP in cm.
    y_mcp : float
        Y coordinate of the MCP in cm.
    z_mcp : float
        Z coordinate of the MCP in cm.

    Returns
    -------
    x_lander : float
        X coordinate of the Lander in cm.
    y_lander : float
        Y coordinate of the Lander in cm.
    z_lander : float
        Z coordinate of the Lander in cm.
    """

    DX_to_BX = np.cos((180 - 55.36) * np.pi / 180)
    DX_to_BY = np.cos((38.17) * np.pi / 180)
    DX_to_BZ = np.cos((75.96) * np.pi / 180)

    DY_to_BX = np.cos((180 - 76.31) * np.pi / 180)
    DY_to_BY = np.cos((116.02) * np.pi / 180)
    DY_to_BZ = np.cos((29.89) * np.pi / 180)

    DZ_to_BX = np.cos((180 - 142.0) * np.pi / 180)
    DZ_to_BY = np.cos((64.19) * np.pi / 180)
    DZ_to_BZ = np.cos((64.19) * np.pi / 180)

    # Rdb rotates vectors from Fb to Fd
    Rdb = np.zeros((3, 3))
    Rdb[0, 0] = DX_to_BX
    Rdb[0, 1] = DX_to_BY
    Rdb[0, 2] = DX_to_BZ
    Rdb[1, 0] = DY_to_BX
    Rdb[1, 1] = DY_to_BY
    Rdb[1, 2] = DY_to_BZ
    Rdb[2, 0] = DZ_to_BX
    Rdb[2, 1] = DZ_to_BY
    Rdb[2, 2] = DZ_to_BZ

    Rbd = Rdb.transpose()

    # Transform the coordinates
    X_mcp = np.array([x_mcp, y_mcp, z_mcp])
    X_lander = Rbd @ X_mcp

    return X_lander[0], X_lander[1], X_lander[2]


def transform_lander_to_lunar(x_lander, y_lander, z_lander):
    """
    Function to transform Lander coordinates to Lunar coordinates

    Parameters
    ----------
    x_lander : float
        X coordinate of the Lander in cm.
    y_lander : float
        Y coordinate of the Lander in cm
    z_lander : float
        Z coordinate of the Lander in cm.

    Returns
    -------
    x_lunar : float
        X coordinate of the Lunar in cm.
    y_lunar : float
        Y coordinate of the Lunar in cm.
    z_lunar : float
        Z coordinate of the Lunar in cm.
    """

    # NOTE: The transformation matrix below is just a place holder. The actual transformation will be
    # updated once we have the actual data.

    # Transformation matrix from Lander to Lunar coordinates
    BX_to_LX = np.cos((180 - 55.36) * np.pi / 180)
    BX_to_BY = np.cos((38.17) * np.pi / 180)
    BX_to_BZ = np.cos((75.96) * np.pi / 180)

    BY_to_LX = np.cos((180 - 76.31) * np.pi / 180)
    BY_to_LY = np.cos((116.02) * np.pi / 180)
    BY_to_LZ = np.cos((29.89) * np.pi / 180)

    BZ_to_LX = np.cos((180 - 142.0) * np.pi / 180)
    BZ_to_LY = np.cos((64.19) * np.pi / 180)
    BZ_to_LZ = np.cos((64.19) * np.pi / 180)

    # Rlb rotates vectors from Fl to Fb
    Rlb = np.zeros((3, 3))
    Rlb[0, 0] = BX_to_LX
    Rlb[0, 1] = BX_to_BY
    Rlb[0, 2] = BX_to_BZ
    Rlb[1, 0] = BY_to_LX
    Rlb[1, 1] = BY_to_LY
    Rlb[1, 2] = BY_to_LZ
    Rlb[2, 0] = BZ_to_LX
    Rlb[2, 1] = BZ_to_LY
    Rlb[2, 2] = BZ_to_LZ

    Rbl = Rlb.transpose()

    # Transform the coordinates
    X_lander = np.array([x_lander, y_lander, z_lander])
    X_lunar = Rbl @ X_lander

    return X_lunar[0], X_lunar[1], X_lunar[2]


def transform_lander_to_j2000(x_lander, y_lander, z_lander):
    """
    Function to transform Lander coordinates to J2000 coordinates

    Parameters
    ----------
    x_lander : float
        X coordinate of the Lander in cm.
    y_lander : float
        Y coordinate of the Lander in cm
    z_lander : float
        Z coordinate of the Lander in cm.

    Returns
    -------
    RA : float
        Right Ascension in degrees.
    Dec : float
        Declination in degrees.
    """

    # NOTE: This is just a placeholder transformation. The actual transformation will depend on the
    # specific orientation of the Lander with respect to the J2000 coordinate system and the time of
    # the observation.

    # Convert Lander coordinates to spherical coordinates
    r = np.sqrt(x_lander**2 + y_lander**2 + z_lander**2)
    RA = np.arctan2(y_lander, x_lander) * 180 / np.pi
    Dec = np.arcsin(z_lander / r) * 180 / np.pi

    return RA, Dec


def level1c_data_processing(df):
    """
    Function to process Level 1C data

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing Level 1C data.

    Returns
    -------
    pandas.DataFrame
        Processed DataFrame with Level 1C data.
    """

    # Transform from MCP to Lander coordinates
    df[["photon_x_lander", "photon_y_lander", "photon_z_lander"]] = df.apply(
        lambda row: transform_mcp_to_lander(
            row["photon_x_mcp"], row["photon_y_mcp"], row["photon_z_mcp"]
        ),
        axis=1,
        result_type="expand",
    )

    # Transform the coordinates from Lander to Lunar
    df[["photon_x_lunar", "photon_y_lunar", "photon_z_lunar"]] = df.apply(
        lambda row: transform_lander_to_lunar(
            row["photon_x_lander"], row["photon_y_lander"], row["photon_z_lander"]
        ),
        axis=1,
        result_type="expand",
    )

    # Transform the coordinates from Lander to J2000
    df[["photon_RA", "photon_Dec"]] = df.apply(
        lambda row: transform_lander_to_j2000(
            row["photon_x_lander"], row["photon_y_lander"], row["photon_z_lander"]
        ),
        axis=1,
        result_type="expand",
    )

    # Keys to return
    key_list = [
        "Epoch",
        "photon_x_mcp",
        "photon_y_mcp",
        "photon_x_lunar",
        "photon_y_lunar",
        "photon_z_lunar",
        "photon_RA",
        "photon_Dec",
    ]
    return df[key_list]


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

    # Save the processed DataFrame to the output file
    sdtc.save_data_to_cdf(
        df=processed_df,
        file_name=output_sci_file_name,
        file_version=f"{primary_version}.{secondary_version}",
    )


def main(start_time=None, end_time=None):
    # Get the list of files in the folder and subfolders
    sci_folder = "/home/cephadrius/Downloads/"

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
start_hour = 19
end_hour = 22
if __name__ == "__main__":
    for month in range(3, 4):
        for day in range(start_date, start_date + 2):
            for hour in range(start_hour, end_hour):
                start_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:00:00Z"
                end_time = f"2025-{month:02d}-{day:02d}T{hour:02d}:59:59Z"
                # print(f"Processing from {start_time} to {end_time}")
                main(start_time=start_time, end_time=end_time)
    # print(f"\n\nProcessing completed for {start_date} from {start_hour} to {end_hour}")
