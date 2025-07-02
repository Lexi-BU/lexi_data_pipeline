import importlib
import datetime
import numpy as np
from dateutil import parser
import get_l1c_files_sci_parallel as gl1c
import pandas as pd
from spacepy.pycdf import CDF as cdf

importlib.reload(gl1c)


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
        if pointing_data.empty:
            raise ValueError(f"No pointing data found for the provided epoch value: {epoch_value}")

    return pointing_data

epoch_value = "2025-03-16T19:00:00Z"
pointing_data = get_body_detector_rotation_matrix(epoch_value)

print(f"Pointing data for epoch {epoch_value}:\n{pointing_data}")