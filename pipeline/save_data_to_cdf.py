import re
from pathlib import Path

import pandas as pd
from spacepy.pycdf import CDF as cdf


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

    # Change the file extension from csv to cdf and add the file version to the file name
    cdf_file = folder_name / file_name.replace(".csv", "_" + file_version + ".cdf")

    # Inside the folder_name, create a folder called "cdf" if it does not exist
    Path(folder_name / "cdf").mkdir(parents=True, exist_ok=True)

    # Inside the folder "cdf" create a folder based on the file_version if it does not exist
    Path(folder_name / "cdf" / file_version).mkdir(parents=True, exist_ok=True)

    # Get the full path of the cdf file
    cdf_file = folder_name / "cdf" / file_version / cdf_file.name
    print(
        f"Creating CDF file: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    )
    print(Path(cdf_file).exists())
    # If the cdf file already exists, overwrite it
    if Path(cdf_file).exists():
        # Raise a warning saying the file already exists and ask the user if they want to
        # overwrite it
        print(
            f"\n \033[1;91m WARNING: \033[91m The CDF file already exists and will be overwritten:\n"
            f"\033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
        )
        Path(cdf_file).unlink()
    # else:
    print(
        f"Creating CDF file: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    )

    # Convert the array to datetime objects in UTC
    df.index = pd.to_datetime(df.index, utc=True, unit="s")

    time_stamp = df.index.astype(int) // 10**9
    time_stamp = time_stamp[0]

    cdf_file = str(cdf_file)

    date_str = cdf_file.split("_")[-5]

    cdf_file = re.sub(re.escape(date_str), str(time_stamp), cdf_file)

    # Check if the cdf file already exists, if it does then remove it
    if Path(cdf_file).exists():
        Path(cdf_file).unlink()

    print(cdf_file)
    cdf_file = str(cdf_file)
    cdf_data = cdf(cdf_file, "")
    cdf_data.attrs["title"] = cdf_file.split("/")[-1].split(".")[0]
    cdf_data.attrs["created"] = str(pd.Timestamp.now())
    cdf_data.attrs["TimeZone"] = "UTC"
    cdf_data.attrs["creator"] = "Ramiz A. Qudsi"
    cdf_data.attrs["source"] = cdf_file
    cdf_data.attrs["source_type"] = "csv"
    cdf_data.attrs["source_format"] = "lxi"
    cdf_data.attrs["source_version"] = file_version
    cdf_data.attrs["source_description"] = "X-ray data from the LEXI spacecraft"
    cdf_data.attrs["source_description_url"] = "TODO"
    cdf_data.attrs["source_description_email"] = "qudsira@bu.edu"
    cdf_data.attrs["source_description_institution"] = "BU"

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
        cdf_data[col] = df[col]
    cdf_data.close()
    print(
        f"\n  CDF file created: \033[1;94m {Path(cdf_file).parent}/\033[1;92m{Path(cdf_file).name} \033[0m"
    )

    return cdf_file
