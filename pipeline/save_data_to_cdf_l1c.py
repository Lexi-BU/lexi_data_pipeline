import datetime
import warnings
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from spacepy.pycdf import CDF as cdf

# Suppress warnings
warnings.filterwarnings("ignore")

StrPath = Union[str, Path]


def save_data_to_cdf(
    df: Optional[pd.DataFrame] = None,
    file_name: Optional[StrPath] = None,
):
    """
    Convert a CSV file to a CDF file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame of the CSV file.
    file_name : str
        Name of the CDF file.
    Returns
    -------
    cdf_file : str
        Path to the CDF file.
    """

    if df is None:
        raise ValueError("`df` must be a valid pandas DataFrame.")
    if file_name is None:
        raise ValueError("`file_name` must be a non-empty string or Path.")
    # Get the folder name and the file name from the file_name using Path
    folder_name = Path(file_name).parent
    file_name = Path(file_name).name

    print(f"Saving data to CDF file: {file_name}")
    print(f"Folder name: {folder_name}")
    # In the folder name, replace "csv" with "cdf"
    folder_name = str(folder_name).replace("csv", "cdf")
    # Convert folder_name to Path
    folder_name = Path(folder_name)
    # Change the file extension from csv to cdf and add the file version to the file name
    cdf_file = folder_name / file_name.replace(".csv", ".cdf")

    # Inside the folder_name, create a folder called "cdf" if it does not exist
    Path(folder_name).mkdir(parents=True, exist_ok=True)

    # Inside the folder "cdf" create a folder based on the file_version if it does not exist
    Path(folder_name).mkdir(parents=True, exist_ok=True)

    # Get the full path of the cdf file
    cdf_file = folder_name / cdf_file.name

    cdf_file = str(cdf_file)

    if Path(cdf_file).exists():
        Path(cdf_file).unlink()

    cdf_file = str(cdf_file)
    cdf_data = cdf(cdf_file, "")
    cdf_data.attrs["TITLE"] = cdf_file.split("/")[-1].split(".")[0]
    cdf_data.attrs["created"] = str(datetime.datetime.now(datetime.timezone.utc))
    cdf_data.attrs["TimeZone"] = "UTC"
    cdf_data.attrs["creator"] = "Ramiz A. Qudsi"
    cdf_data.attrs["source"] = cdf_file.split("/")[-1]
    cdf_data.attrs["source_type"] = "csv"
    cdf_data.attrs["source_format"] = "lxi"
    cdf_data.attrs["source_version"] = "0.1.0"
    cdf_data.attrs["source_description"] = "X-ray data from the LEXI spacecraft"
    cdf_data.attrs["source_description_url"] = "https://lexi-bu.github.io/"
    cdf_data.attrs["source_description_email"] = "leximoon@bu.edu"
    cdf_data.attrs["source_description_institution"] = "Boston_University"

    cdf_data["Epoch"] = df.index
    cdf_data["Epoch_unix"] = df.index.astype(int) // 10**9
    # Set the time zone of the Epoch to UTC
    cdf_data["Epoch"].attrs["TIME_BASE"] = "J2000"
    cdf_data["Epoch"].attrs["FORMAT"] = "yyyy-mm-ddThh:mm:ss.sssZ"
    # Add the Epoch_unix time attribute
    cdf_data["Epoch_unix"].attrs["FORMAT"] = "T"

    cdf_data["Epoch"].attrs["Description"] = "The epoch time in UTC."
    cdf_data["Epoch"].attrs["UNITS"] = "Seconds since 1970-01-01T00:00:00Z"
    cdf_data["Epoch_unix"].attrs["Description"] = "The epoch time in Unix format."
    cdf_data["Epoch_unix"].attrs["UNITS"] = "Seconds since 1970-01-01T00:00:00Z"

    cdf_data["photon_x_mcp"].attrs["Description"] = "The value of the x-axis in mcp coordinates."
    cdf_data["photon_x_mcp"].attrs["UNITS"] = "Centimeters"

    cdf_data["photon_y_mcp"].attrs["Description"] = "The value of the y-axis in mcp coordinates."
    cdf_data["photon_y_mcp"].attrs["UNITS"] = "Centimeters"

    cdf_data["photon_RA"].attrs["Description"] = "The right ascension of the photon in degrees."
    cdf_data["photon_RA"].attrs["UNITS"] = "Degrees"
    cdf_data["photon_Dec"].attrs["Description"] = "The declination of the photon in degrees."
    cdf_data["photon_Dec"].attrs["UNITS"] = "Degrees"
    cdf_data["photon_az"].attrs["Description"] = "The azimuthal angle of the photon in degrees in the local topocentric frame. The angle is measured from the north direction."
    cdf_data["photon_az"].attrs["UNITS"] = "Degrees"
    cdf_data["photon_el"].attrs["Description"] = "The elevation angle of the photon in degrees in the local topocentric frame. The angle is measured from the horizontal plane."
    cdf_data["photon_el"].attrs["UNITS"] = "Degrees"

    cdf_data.close()
    return cdf_file
