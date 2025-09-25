import datetime
import getpass
import glob
import importlib
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import save_modified_data_to_cdf_l1c_istp as sdtc
from dateutil import parser
from spacepy.pycdf import CDF as cdf

importlib.reload(sdtc)

user = getpass.getuser()


def add_centered_counts_per_second_from_index(
    df: pd.DataFrame, out_col: str = "lexi_counts_per_sec"
) -> pd.DataFrame:
    """
    Add a column with the number of events in a centered 1-second window around each row's Epoch.
    Works with DatetimeIndex (UTC). Returns df with a new float64 column out_col.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("DataFrame index must be a DatetimeIndex (UTC).")

    # Fast path: monotonic increasing index → use time-based rolling
    if df.index.is_monotonic_increasing:
        ones = pd.Series(1.0, index=df.index)  # float for REAL8 downstream
        # Centered 1-second window [t-0.5s, t+0.5s]
        counts = ones.rolling("1s", center=True).sum()
        df[out_col] = counts.to_numpy(dtype=np.float64)
        return df

    # Fallback: non-monotonic index → two-pointer on int64 nanoseconds
    t_ns = df.index.view("int64")  # ns since epoch as int64
    n = len(t_ns)
    idx = np.arange(n)

    # Sort by time (stable), remember how to map back
    order = np.argsort(t_ns, kind="mergesort")
    t_sorted = t_ns[order].astype(np.float64) / 1e9  # seconds, float64
    left = right = 0
    counts_sorted = np.empty(n, dtype=np.int32)

    for j in range(n):
        center = t_sorted[j]
        low = center - 0.5
        high = center + 0.5
        while left < n and t_sorted[left] < low:
            left += 1
        while right < n and t_sorted[right] <= high:
            right += 1
        counts_sorted[j] = right - left

    # Unscramble counts back to original row order
    inv = np.empty(n, dtype=np.int64)
    inv[order] = np.arange(n, dtype=np.int64)
    counts = counts_sorted[inv].astype(np.float64)

    df[out_col] = counts
    return df


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

    # Declare the Data_type for each variable
    data_format_dict_lexi = {
        # "Epoch": "CDF_EPOCH",
        "Unix_time": np.float64,
        "photon_x_mcp": np.float32,
        "photon_y_mcp": np.float32,
        "photon_RA": np.float64,
        "photon_Dec": np.float64,
        "photon_az": np.float64,
        "photon_el": np.float64,
        "lexi_counts_per_sec": np.float64,
    }
    data_format_dict_eph = {
        # "lexi_sc_eph_epoch": "CDF_EPOCH",
        "lexi_sc_pos_gse_x": np.float64,
        "lexi_sc_pos_gse_y": np.float64,
        "lexi_sc_pos_gse_z": np.float64,
        "moon_pos_gse_x": np.float64,
        "moon_pos_gse_y": np.float64,
        "moon_pos_gse_z": np.float64,
        "sza": np.float64,
    }
    if user == "cephadrius":
        l1c_sci_folder = "/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf/"
    elif user == "vetinari":
        l1c_sci_folder = "/home/vetinari/Desktop/git/Lexi-Bu/lexi_data_pipeline/data/L1c/sci/cdf/"
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

    # Epoch from ephemeris file to be added to CDF
    eph_file = f"/home/{user}/Desktop/git/Lexi-BU/lexi_data_pipeline/data/ephemeris_data/LEXIAngleData_ACTUAL_20250723_10min_linear.csv"
    df_eph = pd.read_csv(eph_file, parse_dates=["Epoch"], index_col="Epoch")
    df_eph.index = pd.to_datetime(df_eph.index).tz_convert("UTC")
    # Rename the index to lexi_sc_eph_epoch
    # Read the CDF files and convert to DataFrames
    for file_name in l1c_sci_files[:]:
        print(f"Processing file: {file_name}")
        data_df = read_cdf_files_to_dataframes(file_name)

        # Count the number observations each second
        # data_df["lexi_counts_per_sec"] = data_df.groupby(data_df.index).cumcount() + 1
        data_df = add_centered_counts_per_second_from_index(data_df, out_col="lexi_counts_per_sec")

        # Select the data between the specified start and end times
        if start_time is not None and end_time is not None:
            start_dt = parser.parse(start_time).replace(tzinfo=datetime.timezone.utc)
            end_dt = parser.parse(end_time).replace(tzinfo=datetime.timezone.utc)
            data_df = data_df[(data_df.index >= start_dt) & (data_df.index <= end_dt)]
            eph_df = df_eph[(df_eph.index >= start_dt) & (df_eph.index <= end_dt)]

        # return data_df, eph_df, file_name
        # Ensure that the keys are in correct format
        data_df = data_df[list(data_format_dict_lexi.keys())].astype(data_format_dict_lexi)
        eph_df = eph_df[list(data_format_dict_eph.keys())].astype(data_format_dict_eph)

        # Save the DataFrame to a new CDF file
        # Get the modified L1C SCI folder path same as the stem of the original file
        modified_l1c_sci_folder = Path(file_name).parent
        cdf_file = sdtc.save_data_to_cdf(
            df=data_df,
            df_eph=eph_df,
            output_dir=modified_l1c_sci_folder,
            version=0,
            logical_source="clps-bgm1_lexi_l1c-photons",
        )
        print(f"Saved modified CDF file: {cdf_file}")

    return (l1c_sci_files, data_df, cdf_file)


start_date = "2025-03-16T21:00:00"
end_date = "2025-03-16T21:15:00"
if __name__ == "__main__":
    results = main(start_time=start_date, end_time=end_date)

dat_r = cdf(results[-1])

print(dat_r)

print(dat_r.attrs)

print(len(dat_r.attrs))

# Copy the new created file to
# "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l1c"
shutil.copy(
    results[-1],
    f"/home/{user}/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l1c/",
)
