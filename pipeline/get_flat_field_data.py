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
import save_data_to_cdf_l1c_istp as sdtc
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
        +
        #     "lexi_look_direction_data_uninterpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
        "lexi_look_direction_data_resampled_interpolated_2025-03-02_00-00-00_to_2025-03-16_23-59-59_v0.0.csv"
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
        # closest_epoch_value = df_pointing.index[closest_index]
        if pointing_data.empty:
            print(f"No pointing data found for the provided epoch value: {epoch_value}")
    else:
        # Set the pointing data to the first row if no epoch_value is provided
        pointing_data = df_pointing.iloc[0:1]

    RA, Dec = pointing_data[["ra_lexi", "dec_lexi"]].values[0]

    # print(
    #     f"RA: {RA}, Dec: {Dec}"
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
        quaternion_type="actual", epoch_value=epoch_value
    )
    V_body_actual = R_b_J2000 @ V_J2000.T

    theta_1 = np.arctan2(-V_body_actual[1], V_body_actual[2]) / deg2rad
    theta_2 = np.asin(V_body_actual[0] / np.linalg.norm(V_body_actual)) / deg2rad
    theta_3 = 157.3949  # This is the roll and and is fixed for the LEXI spacecraft

    R_db_matrix = compute_R_db(theta_1 * deg2rad, theta_2 * deg2rad, theta_3 * deg2rad)

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
        quaternion_value = df_quaternions.iloc[closest_index]

        if quaternion_value.empty:
            # raise ValueError(
            #     f"No quaternion data found for the provided epoch value: {epoch_value}"
            # )
            quaternion_value = quaternion_value.iloc[0]
        # print(f"Quaternion value:\n{quaternion_value.values}")
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


def compute_ra_dec_fixed_epoch(
    X_detector_array: np.ndarray, central_epoch
) -> tuple[np.ndarray, np.ndarray]:
    """
    Vectorized RA/Dec computation for many detector vectors, using a single epoch.

    Parameters
    ----------
    X_detector_array : (N, 3) float array
        Detector-frame vectors (x,y,z) for N photons.
    central_epoch : str | pd.Timestamp | np.datetime64 | datetime
        Timestamp used to compute a single rotation for all photons.

    Returns
    -------
    RA, Dec : (N,) float arrays in degrees
    """
    # Get rotation once at the central epoch
    R_J2000_d = get_rotation_matrix_detector_to_J2000(epoch_value=central_epoch)

    # Transform all vectors to J2000 frame in one shot: (3x3) @ (3xN) -> (3xN) -> (N,3)
    X_J2000 = (R_J2000_d @ X_detector_array.T).T  # shape (N, 3)

    # RA = atan2(y, x); Dec = arcsin(z / ||v||)
    x = X_J2000[:, 0]
    y = X_J2000[:, 1]
    z = X_J2000[:, 2]
    norm = np.linalg.norm(X_J2000, axis=1)

    RA = np.arctan2(y, x) / deg2rad
    Dec = np.arcsin(z / norm) / deg2rad
    return RA, Dec


def fast_transform_fixed_epoch(
    central_epoch: pd.Timestamp, random_seed: int = 42, n_photons: int | str = "all"
) -> tuple[np.ndarray, np.ndarray]:

    flat_field_file = "/media/cephadrius/lexi_data/lexi_data/flat_field_data/lexi_l1c_flat_field_data_20240524_20240530.cdf"

    with cdf(flat_field_file) as ff:
        x = ff["photon_x_mcp"][:]
        y = ff["photon_y_mcp"][:]

    if n_photons == "all":
        n_photons = len(x)
    elif n_photons > len(x):
        n_photons = len(x)
    rng = np.random.default_rng(random_seed)
    idx = rng.choice(len(x), size=n_photons, replace=False)

    df = pd.DataFrame(
        {
            "photon_x_mcp": x[idx],
            "photon_y_mcp": y[idx],
            "photon_z_mcp": 37.5,  # broadcast scalar
        }
    )

    # Apply mask in NumPy
    mask = (np.abs(x) <= 4.5) & (np.abs(y) <= 4.5)

    x, y = x[mask], y[mask]

    # Prepare inputs once
    X = df[["photon_x_mcp", "photon_y_mcp", "photon_z_mcp"]].to_numpy()

    # One rotation for all rows
    R = get_rotation_matrix_detector_to_J2000(epoch_value=central_epoch)

    # (N,3) = (N,3) @ (3,3)^T  OR  (R @ X.T).T — either is fine
    Xj = (R @ X.T).T

    x, y, z = Xj[:, 0], Xj[:, 1], Xj[:, 2]
    n = np.linalg.norm(Xj, axis=1)

    RA = np.arctan2(y, x) / deg2rad
    Dec = np.arcsin(z / n) / deg2rad

    # out = df.copy()
    # out["photon_RA"] = RA
    # out["photon_Dec"] = Dec
    # return out[["photon_RA", "photon_Dec"]]
    return (RA, Dec)
