import datetime
import glob
import importlib

import get_l1c_files_sci_parallel as tlxf
import numpy as np
import pandas as pd
import pytz
from dateutil import parser

importlib.reload(tlxf)

quaternion_type = "actual"
epoch_value = "2025-03-03T00:01:29Z"
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
rotation_matrix_b_J2000 = tlxf.quaternions_to_rotation_matrix(quaternion_value.values)
