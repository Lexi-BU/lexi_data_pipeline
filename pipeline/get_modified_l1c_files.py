import datetime
import glob
import importlib
import re
from pathlib import Path

import pandas as pd
import save_modified_data_to_cdf_l1c_istp as sdtc
from dateutil import parser
from spacepy.pycdf import CDF as cdf
from tqdm import tqdm

importlib.reload(sdtc)


def read_cdf_files_to_dataframes(file_name):
    """
    Read a CDF file and convert its variables to pandas DataFrames.

    Parameters
    ----------
    file_name : str or Path
        Path to the CDF file.

    Returns
    -------
    dict
        Dictionary with variable names as keys and corresponding pandas DataFrames as values.
    """
    data = {}
    with cdf(file_name) as cdf_file:
        for var in cdf_file:
            try:
                var_data = cdf_file[var][...]
                if var_data.ndim == 1:
                    df = pd.DataFrame(var_data, columns=[var])
                else:
                    df = pd.DataFrame(var_data)
                    df.columns = [f"{var}_{i}" for i in range(var_data.shape[1])]
                data[var] = df
            except Exception as e:
                print(f"Error reading variable {var} from {file_name}: {e}")

    data_df = pd.DataFrame()
    for _, df in data.items():
        data_df = pd.concat([data_df, df], axis=1)

    # Set the index to the 'Epoch' variable if it exists
    if "Epoch" in data:
        # Set the epoch column as index
        data_df.set_index("Epoch", inplace=True)
        # Convert the index from datetime64 to datetime objects and set the timezone to UTC
        data_df.index = pd.to_datetime(data_df.index).tz_localize("UTC")

    # Rename the "Epoch_unix" column to "Unix_time" if it exists
    if "Epoch_unix" in data_df.columns:
        data_df.rename(columns={"Epoch_unix": "Unix_time"}, inplace=True)
    return data_df


def main(start_time: str = None, end_time: str = None):

    l1c_sci_folder = "/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf/"
    # Get all files in the folder and subfolders
    l1c_sci_files = sorted(glob.glob(f"{l1c_sci_folder}/**/*.cdf", recursive=True))
    print(f"Found {len(l1c_sci_files)} total L1C SCI files.")

    # Filter files based on start and end time if provided
    if start_time is not None and end_time is not None:
        start_dt = parser.parse(start_time)
        end_dt = parser.parse(end_time)
        filtered_files = []
        for file in l1c_sci_files:
            match = re.search(r"_(\d{10})_V\d+\.\d+\.cdf$", file)
            if match:
                file_time_str = match.group(1)
                file_time = datetime.datetime.strptime(file_time_str, "%Y%m%d%H")
                if start_dt <= file_time <= end_dt:
                    filtered_files.append(file)
        l1c_sci_files = filtered_files
    print(f"Found {len(l1c_sci_files)} L1C SCI files in the specified time range.")

    # Read the CDF files and convert to DataFrames
    for file_name in l1c_sci_files[:]:
        print(f"Processing file: {file_name}")
        data_df = read_cdf_files_to_dataframes(file_name)

        # Select the data between the specified start and end times
        if start_time is not None and end_time is not None:
            start_dt = parser.parse(start_time).replace(tzinfo=datetime.timezone.utc)
            end_dt = parser.parse(end_time).replace(tzinfo=datetime.timezone.utc)
            data_df = data_df[(data_df.index >= start_dt) & (data_df.index <= end_dt)]

        # Save the DataFrame to a new CDF file
        # Get the modified L1C SCI folder path same as the stem of the original file
        modified_l1c_sci_folder = Path(file_name).parent
        cdf_file = sdtc.save_data_to_cdf(
            df=data_df,
            output_dir=modified_l1c_sci_folder,
            version=0,
            logical_source="clps-bgm1_lexi_l1c-photons",
        )

    return (l1c_sci_files, data_df, cdf_file)


start_date = "2025-03-16T16:00:00"
end_date = "2025-03-16T22:05:00"
if __name__ == "__main__":
    results = main(start_time=start_date, end_time=end_date)
