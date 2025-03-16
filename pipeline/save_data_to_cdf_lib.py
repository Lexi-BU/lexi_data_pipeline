import re
import shutil
import tempfile
import warnings
from pathlib import Path

import cdflib
import pandas as pd

# Suppress warnings
warnings.filterwarnings("ignore")


def save_data_to_cdf(df=None, file_name=None, file_version="0.0"):
    """
    Convert a DataFrame to a CDF file using cdflib.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame of the CSV file.
    file_name : str
        Name of the CDF file.
    file_version : str
        Version of the CDF file (default is "0.0").

    Returns
    -------
    cdf_file : str
        Path to the CDF file.
    """
    # Ensure the DataFrame is not empty
    if df is None or df.empty:
        raise ValueError("DataFrame is empty or None.")

    # Handle null values
    if df.isnull().values.any():
        print("Warning: DataFrame contains null values. Filling nulls with zeros.")
        df = df.fillna(0)

    # Ensure the index is timezone-aware
    # df.index = pd.to_datetime(df.index).tz_localize("UTC")

    # Get the folder name and the file name from the file_name using Path
    folder_name = Path(file_name).parent
    file_name = Path(file_name).name

    # In the folder name, replace "csv" with "cdf"
    folder_name = str(folder_name).replace("csv", "cdf")
    folder_name = Path(folder_name)
    cdf_file = folder_name / file_name.replace(".csv", ".cdf")

    # Create the output folder if it doesn't exist
    folder_name.mkdir(parents=True, exist_ok=True)

    # Use a temporary file to avoid overwriting issues
    temp_cdf_file = str(cdf_file.with_suffix(".tmp.cdf"))
    if Path(cdf_file).exists():
        Path(cdf_file).unlink()

    try:
        # Create the CDF file using cdflib
        cdf_data = cdflib.CDF(temp_cdf_file, create=True)

        # Add global attributes
        cdf_data.attrs["title"] = cdf_file.stem
        cdf_data.attrs["created"] = str(pd.Timestamp.now())
        cdf_data.attrs["TimeZone"] = "UTC"
        cdf_data.attrs["creator"] = "Ramiz A. Qudsi"
        cdf_data.attrs["source"] = cdf_file.name
        cdf_data.attrs["source_type"] = "csv"
        cdf_data.attrs["source_format"] = "lxi"
        cdf_data.attrs["source_version"] = "0.1.0"
        cdf_data.attrs["source_description"] = "X-ray data from the LEXI spacecraft"
        cdf_data.attrs["source_description_url"] = "https://lexi-bu.github.io/"
        cdf_data.attrs["source_description_email"] = "leximoon@bu.edu"
        cdf_data.attrs["source_description_institution"] = "Boston_University"

        # Add Epoch and Epoch_unix
        cdf_data.write("Epoch", df.index.astype("datetime64[ns]"))
        cdf_data.write("Epoch_unix", (df.index.astype(int) // 10**9).astype("int64"))

        # Add variable attributes for Epoch
        cdf_data.varattsget("Epoch")["TIME_BASE"] = "J2000"
        cdf_data.varattsget("Epoch")["FORMAT"] = "yyyy-mm-ddThh:mm:ss.sssZ"
        cdf_data.varattsget("Epoch_unix")["FORMAT"] = "T"

        # Add other columns
        for col in df.columns:
            if col in ["utc_time", "local_time"]:
                df[col] = pd.to_datetime(df[col], utc=True)
            cdf_data.write(col, df[col].values)

        # Close the CDF file
        cdf_data.close()

        # Rename the temporary file to the final file name
        shutil.move(temp_cdf_file, cdf_file)
        print(
            f"\n  CDF file created: \033[1;94m {cdf_file.parent}/\033[1;92m{cdf_file.name} \033[0m"
        )

    except Exception as e:
        print(f"Error creating CDF file: {e}")
        raise

    return str(cdf_file)
