import datetime
import re
import warnings
from pathlib import Path

import pandas as pd
from spacepy.pycdf import CDF as cdf

# Suppress warnings
warnings.filterwarnings("ignore")


def save_data_to_cdf(df=None, file_name=None, file_version="0.0"):
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
    # print(
    #     f"Creating CDF file: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    # )

    # If the cdf file already exists, overwrite it
    if Path(cdf_file).exists():
        # Raise a warning saying the file already exists and ask the user if they want to
        # overwrite it
        # print(
        #     f"\n \033[1;91m WARNING: \033[91m The CDF file already exists and will be overwritten:\n"
        #     f"\033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
        # )
        Path(cdf_file).unlink()
    # else:
    # print(
    #     f"Creating CDF file: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    # )

    time_stamp = df.index.astype(int) // 10**9
    time_stamp = time_stamp[0]

    cdf_file = str(cdf_file)

    if Path(cdf_file).exists():
        Path(cdf_file).unlink()

    cdf_file = str(cdf_file)
    cdf_data = cdf(cdf_file, "")
    cdf_data.attrs["title"] = cdf_file.split("/")[-1].split(".")[0]
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

    for col in df.columns:
        # If the column is either "utc_time" or "local_time", convert it to a datetime object and
        # then to a CDF variable
        if col == "utc_time" or col == "local_time":
            df[col] = pd.to_datetime(df[col], utc=True)
            cdf_data[col] = df[col]
        else:
            cdf_data[col] = df[col]

    cdf_data["Epoch"].attrs["Description"] = "The epoch time in UTC."
    cdf_data["Epoch"].attrs["units"] = "Seconds since 1970-01-01T00:00:00Z"
    cdf_data["Epoch_unix"].attrs["Description"] = "The epoch time in Unix format."
    cdf_data["Epoch_unix"].attrs["units"] = "Seconds since 1970-01-01T00:00:00Z"

    cdf_data["photon_x_mcp"].attrs["Description"] = "The value of the x-axis in mcp coordinates."
    cdf_data["photon_x_mcp"].attrs["units"] = "Centimeters"

    cdf_data["photon_y_mcp"].attrs["Description"] = "The value of the y-axis in mcp coordinates."
    cdf_data["photon_y_mcp"].attrs["units"] = "Centimeters"

    cdf_data["photon_RA"].attrs["Description"] = "The right ascension of the photon in degrees."
    cdf_data["photon_RA"].attrs["units"] = "Degrees"
    cdf_data["photon_Dec"].attrs["Description"] = "The declination of the photon in degrees."
    cdf_data["photon_Dec"].attrs["units"] = "Degrees"
    cdf_data["photon_x_lunar"].attrs[
        "Description"
    ] = "The value of the x-axis in lunar coordinates."
    cdf_data["photon_x_lunar"].attrs["units"] = "Centimeters"
    cdf_data["photon_y_lunar"].attrs[
        "Description"
    ] = "The value of the y-axis in lunar coordinates."
    cdf_data["photon_y_lunar"].attrs["units"] = "Centimeters"
    cdf_data["photon_z_lunar"].attrs[
        "Description"
    ] = "The value of the z-axis in lunar coordinates."
    cdf_data["photon_z_lunar"].attrs["units"] = "Centimeters"

    cdf_data.close()
    # print(
    #     f"\n  CDF file created: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    # )

    return cdf_file
