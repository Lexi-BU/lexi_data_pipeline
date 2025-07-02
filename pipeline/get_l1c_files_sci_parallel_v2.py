import datetime
import glob
import importlib
import re
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
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


def compute_R_db(theta1, theta2, theta3):
    c1, c2, c3 = np.cos([theta1, theta2, theta3])
    s1, s2, s3 = np.sin([theta1, theta2, theta3])

    R = np.array(
        [
            [c3 * c2, c3 * s2 * s1 + s3 * c1, -c3 * s2 * c1 + s3 * s1],
            [-s3 * c2, -s3 * s2 * s1 + c3 * c1, s3 * s2 * c1 + c3 * s1],
            [s2, -c2 * s1, c2 * c1],
        ]
    )

    return R


def get_body_detector_rotation_matrix(epoch_value=None):
    """
    Get the rotation matrices for transforming coordinates from MCP to Lander and Lunar frames.
    """
    pointing_folder = "../data/pointing/"
    pointing_file = (
        pointing_folder
        + "lexi_look_direction_data_uninterpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
    )

    df_pointing = pd.read_csv(pointing_file, index_col=None)

    # Convert Epoch to datetime and set as index
    df_pointing["Epoch"] = pd.to_datetime(df_pointing["Epoch"], format="mixed", utc=True)
    df_pointing.set_index("Epoch", inplace=True)
    df_pointing.sort_index(inplace=True)

    if epoch_value is not None:
        # Set the timezone of the epoch_value to UTC
        if isinstance(epoch_value, str):
            epoch_value = parser.parse(epoch_value)
        elif isinstance(epoch_value, datetime.datetime):
            # If epoch_value is already a datetime object, ensure it is timezone-aware
            if epoch_value.tzinfo is None:
                epoch_value = epoch_value.replace(tzinfo=pytz.UTC)

        # Convert from numpy.datetime64 to pandas datetime
        if isinstance(epoch_value, np.datetime64):
            epoch_value = pd.to_datetime(epoch_value).tz_localize("UTC")
        elif isinstance(epoch_value, pd.Timestamp):
            # If epoch_value is already a pandas Timestamp, ensure it is timezone-aware
            if epoch_value.tzinfo is None:
                epoch_value = epoch_value.tz_localize("UTC")
        elif isinstance(epoch_value, pd.DatetimeIndex):
            # If epoch_value is a DatetimeIndex, convert it to a single timestamp
            epoch_value = epoch_value[0].tz_localize("UTC")

        closest_index = df_pointing.index.get_indexer([epoch_value], method="nearest")[0]
        pointing_data = df_pointing.iloc[closest_index : closest_index + 1]
        # Get the epoch value corresponding to the closest index
        closest_epoch_value = df_pointing.index[closest_index]
        if pointing_data.empty:
            raise ValueError(f"No pointing data found for the provided epoch value: {epoch_value}")
    # else:
    #     # Set the pointing data to the first row if no epoch_value is provided
    #     pointing_data = df_pointing.iloc[0:1]

    RA, Dec = pointing_data[["ra_lexi", "dec_lexi"]].values[0]

    # print(
    #     f"RA: {RA}, Dec: {Dec}, Closest Epoch: {closest_epoch_value}, Actual epoch: {epoch_value}"
    # )

    # Get the V_J2000 vector
    V_J2000 = np.array(
        [
            np.cos(RA * deg2rad) * np.cos(Dec * deg2rad),
            np.sin(Dec * deg2rad),
            np.sin(RA * deg2rad) * np.cos(Dec * deg2rad),
        ]
    )

    R_b_J2000 = convert_quaternions_to_rotation_matrix(
        quaternion_type="actual", epoch_value=closest_epoch_value
    )

    V_body_actual = R_b_J2000 @ V_J2000.T

    theta_1 = np.arctan2(-V_body_actual[1], V_body_actual[2]) / deg2rad
    theta_2 = np.asin(V_body_actual[0] / np.linalg.norm(V_body_actual)) / deg2rad
    theta_3 = 157.3949  # This is the roll and and is fixed for the LEXI spacecraft

    R_db_matrix = compute_R_db(theta_1 * deg2rad, theta_2 * deg2rad, theta_3 * deg2rad)

    # theta_test = np.arctan2(-R_db_matrix[1, 0], R_db_matrix[0, 0]) / deg2rad
    # print(f"Theta_test: {theta_test}, Expected Theta_3: {theta_3}")
    # print(f"Theta1 : {theta_1}, Theta2: {theta_2}, Theta3: {theta_test}")
    return R_db_matrix


def quaternions_to_rotation_matrix(q):
    """
    Convert quaternions to rotation matrices.

    Parameters
    ----------
    quaternions : np.ndarray
        Array of shape (N, 4) where N is the number of quaternions.
        Each quaternion is represented as [q0, q1, q2, q3].

    Returns
    -------
    np.ndarray
        Rotation matrix of shape (N, 3, 3).
    """

    # Compute the rotation matrix from the quaternion components
    R = np.empty((3, 3))

    R[0, 0] = q[0] ** 2 + q[1] ** 2 - q[2] ** 2 - q[3] ** 2
    R[0, 1] = 2 * (q[1] * q[2] + q[0] * q[3])
    R[0, 2] = 2 * (q[1] * q[3] - q[0] * q[2])
    R[1, 0] = 2 * (q[1] * q[2] - q[0] * q[3])
    R[1, 1] = q[0] ** 2 - q[1] ** 2 + q[2] ** 2 - q[3] ** 2
    R[1, 2] = 2 * (q[2] * q[3] + q[0] * q[1])
    R[2, 0] = 2 * (q[1] * q[3] + q[0] * q[2])
    R[2, 1] = 2 * (q[2] * q[3] - q[0] * q[1])
    R[2, 2] = q[0] ** 2 - q[1] ** 2 - q[2] ** 2 + q[3] ** 2

    return R


def convert_quaternions_to_rotation_matrix(quaternion_type="actual", epoch_value=None):
    """
    Convert quaternions to rotation matrices.

    Parameters
    ----------
    quaternion_type : str, optional
        Type of quaternion representation. Default is "actual". The other option is "nominal".

    epoch_value : str, optional
        The epoch value to find the closest quaternion. If None, the first quaternion is used.

    Returns
    -------
    rotation_matrix : np.ndarray
        Rotation matrix of shape (3, 3) corresponding to the quaternion at the specified epoch value.
    If epoch_value is None, the first quaternion is used.
    Raises
    ------
    ValueError
        If no quaternion data is found for the provided epoch value or if the quaternion data contains NaN values.
    If the epoch_value is not provided, the first quaternion is used.
    If the quaternion file does not exist, an error is raised.
    If the quaternion data contains NaN values, an error is raised.
    If the epoch_value is not in the correct format, an error is raised.
    If the quaternion_type is not "actual" or "nominal", an error is raised
    """

    quaternion_folder = "../data/quaternions/"
    all_files = sorted(glob.glob(str(quaternion_folder) + "*.csv"))
    if quaternion_type == "actual":
        quaternion_file_name = [f for f in all_files if "Actual" in f]
    else:
        quaternion_file_name = [f for f in all_files if "Nominal" in f]

    df_quaternions = pd.read_csv(quaternion_file_name[0], index_col=None)

    # Drop the "Epoch_MJD" column if it exists
    if "Epoch_MJD" in df_quaternions.columns:
        df_quaternions.drop(columns=["Epoch_MJD"], inplace=True)
    # Convert Epoch_UTC to datetime and set as index
    df_quaternions["Epoch_UTC"] = pd.to_datetime(
        df_quaternions["Epoch_UTC"].str.slice(0, -3), format="mixed", utc=True
    )
    df_quaternions.set_index("Epoch_UTC", inplace=True)

    df_quaternions.sort_index(inplace=True)

    if epoch_value is not None:
        # print(f"Finding quaternion for epoch value: {epoch_value}")
        # print(f"The type of epoch_value is: {type(epoch_value)}")

        # epoch_value = parser.parse(epoch_value)
        # Set the timezone of the epoch_value to UTC
        if isinstance(epoch_value, str):
            epoch_value = parser.parse(epoch_value)
        elif isinstance(epoch_value, datetime.datetime):
            # If epoch_value is already a datetime object, ensure it is timezone-aware
            if epoch_value.tzinfo is None:
                epoch_value = epoch_value.replace(tzinfo=pytz.UTC)

        # Convert from numpy.datetime64 to pandas datetime
        if isinstance(epoch_value, np.datetime64):
            epoch_value = pd.to_datetime(epoch_value).tz_localize("UTC")
        elif isinstance(epoch_value, pd.Timestamp):
            # If epoch_value is already a pandas Timestamp, ensure it is timezone-aware
            if epoch_value.tzinfo is None:
                epoch_value = epoch_value.tz_localize("UTC")
        elif isinstance(epoch_value, pd.DatetimeIndex):
            # If epoch_value is a DatetimeIndex, convert it to a single timestamp
            epoch_value = epoch_value[0].tz_localize("UTC")

        # closest_index = df_quaternions.index.get_loc(epoch_value, method="nearest")
        closest_index = df_quaternions.index.get_indexer(
            [epoch_value], method="nearest", tolerance=pd.Timedelta("5min")
        )[0]
        quaternion_value = df_quaternions.iloc[closest_index : closest_index + 1]
        if quaternion_value.empty:
            raise ValueError(
                f"No quaternion data found for the provided epoch value: {epoch_value}"
            )
        quaternion_value = quaternion_value.iloc[0]
        # print(f"Quaternion value:\n{quaternion_value.values}")
        if quaternion_value.isnull().any():
            raise ValueError(
                f"Quaternion data contains NaN values for the provided epoch value: {epoch_value}"
            )
            print(f"Quaternion value after checking for NaN: {quaternion_value}")
    else:
        # If no epoch_value is provided, use the entire DataFrame
        quaternion_value = df_quaternions.iloc[0]

    # Convert quaternion to rotation matrix
    rotation_matrix_b_J2000 = quaternions_to_rotation_matrix(quaternion_value.values)
    return rotation_matrix_b_J2000


def get_rotation_matrix_detector_to_J2000(quaternion_type="actual", epoch_value=None):
    """
    Get the rotation matrix from the detector frame to the J2000 frame.

    Parameters
    ----------
    quaternion_type : str, optional
        Type of quaternion representation. Default is "actual". The other option is "nominal".

    epoch_value : str, optional
        The epoch value to find the closest quaternion. If None, the first quaternion is used.

    Returns
    -------
    np.ndarray
        Rotation matrix of shape (3, 3) corresponding to the quaternion at the specified epoch value.
    """
    R_db = get_body_detector_rotation_matrix(epoch_value=epoch_value)
    R_b_J2000 = convert_quaternions_to_rotation_matrix(quaternion_type, epoch_value)

    R_d_J2000 = R_db @ R_b_J2000

    R_J2000_d = R_d_J2000.T
    return R_J2000_d


def compute_ra_dec_and_lunar(X_detector=np.array([0, 0, 1]), epoch_value=None):
    """
    Compute the Right Ascension (RA) and Declination (Dec) from the detector coordinates.

    Parameters
    ----------
    X_detector : np.ndarray
        Detector coordinates of shape (1, 3).

    epoch_value : str, optional
        The epoch value to find the closest quaternion. If None, the first quaternion is used.

    Returns
    -------
    RA : np.ndarray
        Right Ascension in degrees.
    Dec : np.ndarray
        Declination in degrees.
    """
    # Set the timezone of the epoch_value to UTC
    # if epoch_value is not None:
    #     epoch_value = epoch_value.replace(tzinfo=pytz.UTC)
    # Get the rotation matrix from the detector frame to the J2000 frame
    R_J2000_d = get_rotation_matrix_detector_to_J2000(epoch_value=epoch_value)

    # Get the rotation matrix from the body nominal frame to the J2000 frame
    R_b_nominal_J2000 = convert_quaternions_to_rotation_matrix(
        quaternion_type="nominal", epoch_value=epoch_value
    )

    # Transform to J2000 frame
    X_J2000 = R_J2000_d @ X_detector.T

    # Compute RA and Dec
    RA = np.arctan2(X_J2000[1], X_J2000[0]) / deg2rad
    Dec = np.arcsin(X_J2000[2] / np.linalg.norm(X_J2000)) / deg2rad

    # Get the rotation matrix from the detector frame to body nominal frame (also referred to as
    # topocentric frame)
    R_b_nominal_detector = R_b_nominal_J2000 @ R_J2000_d

    # Transform MCP coordinates to lunar coordinates
    X_lunar = R_b_nominal_detector @ X_detector.T

    # Get the componenets from the X_lunar
    X_lunar_x = X_lunar[0]
    X_lunar_y = X_lunar[1]
    X_lunar_z = X_lunar[2]

    az = -np.arctan2(-X_lunar_y, X_lunar_z) / deg2rad + 270
    el = np.arcsin(X_lunar_x / np.linalg.norm(X_lunar)) / deg2rad

    # print(f"az: {az}, el: {el}")
    return RA, Dec, X_lunar_x, X_lunar_y, X_lunar_z, az, el


def level1c_data_processing_parallel(df, n_processes=None):
    """
    Parallelized version of level1c_data_processing that computes RA/Dec and lunar coordinates
    for all photons in the dataframe.

    Args:
        df: Input pandas DataFrame containing photon data
        n_processes: Number of processes to use (default: all available CPUs)

    Returns:
        Processed DataFrame with additional columns
    """
    if n_processes is None:
        n_processes = cpu_count() - 1  # Leave one CPU free for the main process

    X_mcp = df[["photon_x_mcp", "photon_y_mcp", "photon_z_mcp"]].to_numpy()
    try:
        df["Epoch"] = pd.to_datetime(df["Epoch"]).dt.tz_localize("UTC")
    except Exception:
        df["Epoch"] = pd.to_datetime(df["Epoch"]).dt.tz_convert("UTC")

    epochs = df["Epoch"].values
    data = list(zip(X_mcp, epochs))

    # Compute RA and Dec in parallel
    print("Computing RA and Dec for all photons...")
    with Pool(n_processes) as pool:
        ra_dec_results = pool.starmap(compute_ra_dec_and_lunar, data)

    ra_values, dec_values, lunar_coords_x, lunar_coords_y, lunar_coords_z, az_values, el_values = (
        zip(*ra_dec_results)
    )
    df["photon_RA"] = ra_values
    df["photon_Dec"] = dec_values
    df["photon_x_lunar"] = lunar_coords_x
    df["photon_y_lunar"] = lunar_coords_y
    df["photon_z_lunar"] = lunar_coords_z
    df["photon_az"] = az_values
    df["photon_el"] = el_values

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
            "photon_az",
            "photon_el",
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
    combined_df["photon_z_mcp"] = 37.5  # This is the focal length of LEXI optics in cm

    # print(combined_df.head())
    # Apply the Level 1C data processing
    processed_df = level1c_data_processing_parallel(combined_df)

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
start_hour = 19
end_hour = 20

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
