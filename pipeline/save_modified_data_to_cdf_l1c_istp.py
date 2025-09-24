import datetime
import getpass
import warnings
from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
from spacepy.pycdf import CDF as cdf

# Suppress warnings
warnings.filterwarnings("ignore")

StrPath = Union[str, Path]
user = getpass.getuser()


def generate_lexi_cdf_filename(
    start_time: datetime.datetime,
    logical_source: str = "clps-bgm1_lexi_l1c-photons",
    version: int = 0,
    output_dir: Path = Path("."),
) -> Tuple[Path, str]:
    """
    Generate an ISTP-compliant LEXI CDF filename.

    Parameters
    ----------
    start_time : datetime
        Start time of the data (in UTC).
    logical_source : str
        Logical source name, e.g., 'clps-bgm1_lexi_l1c-photons'.
    version : int
        Primary version number.
    output_dir : Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Full path to the generated filename.
    """
    start_str = start_time.strftime("%Y%m%d%H")
    while True:
        version_str = f"v{version:02d}"
        filename = f"{logical_source}_{start_str}_{version_str}.cdf"
        file_path = output_dir / filename

        if not file_path.exists():
            break

        print(f"File {filename} exists. Incrementing version.")
        # Update version
        version += 1
    print(f"Generated CDF filename: {filename} in {output_dir}")
    return (output_dir / filename, version_str)


def save_data_to_cdf(
    df: Optional[pd.DataFrame] = None,
    df_eph: Optional[pd.DataFrame] = None,
    output_dir: Optional[StrPath] = None,
    version: int = 0,
    logical_source: str = "clps-bgm1_lexi_l1c-photons",
):
    """
    Save a DataFrame to a CDF file using a skeleton ISTP-compliant CDF file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with datetime index and photon data columns.
    output_dir : str or Path
        Folder where the CDF file will be saved.
    version : int
        Primary version number.
    logical_source : str
        Logical source name (default: "clps-bgm1_lexi_l1c-photons").

    Returns
    -------
    cdf_file : str
        Path to the saved CDF file.
    """
    if df is None or df.empty:
        raise ValueError("`df` must be a non-empty pandas DataFrame with a datetime index.")
    if output_dir is None:
        raise ValueError("`output_dir` must be provided.")

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = df.index[0].to_pydatetime()

    (cdf_file, version_str) = generate_lexi_cdf_filename(
        start_time=start_time,
        logical_source=logical_source,
        version=version,
        output_dir=output_dir,
    )

    # Path to the read-only skeleton
    skeleton_path = Path(
        f"/home/{user}/Desktop/git/Lexi-Bu/lexi_data_pipeline/spdf_data_documents/l1c/clps-bgm1_lexi_l1c-photons_000000000000_v01.cdf"
    )

    # Load the skeleton in read-only mode
    skeleton_cdf = cdf(str(skeleton_path))

    # Create new writable CDF file (overwrite if exists)
    # if cdf_file.exists():
    #     cdf_file.unlink()
    cdf_data = cdf(str(cdf_file), "")

    # Force COLUMN-major layout before defining any variables
    try:
        cdf_data.col_major(True)  # preferred SpacePy API
    except AttributeError:
        cdf_data.majority = "COLUMN"  # fallback on some versions
    # Copy global attributes from skeleton
    for key in skeleton_cdf.attrs:
        cdf_data.attrs[key] = skeleton_cdf.attrs[key][...]

        # Remove following attributes, if present, from the file
        attributes_to_remove = ["Acknowledgement", "Time_resolution", "Rules_of_use"]
        for attr in attributes_to_remove:
            if attr in cdf_data.attrs:
                del cdf_data.attrs[attr]

    # Update dynamic global attributes
    cdf_data.attrs.update(
        {
            "Generation_date": str(datetime.datetime.now(datetime.timezone.utc)),
            "Logical_file_id": cdf_file.stem,
            "Logical_source": "clps-bgm1_lexi_l1c-photons",
            "Data_version": version_str,
        }
    )
    # ========== Variables ==========
    cdf_data["Epoch"] = df.index
    cdf_data["lexi_sc_eph_epoch"] = df_eph.index

    # Convert index to signed 32-bit integers (seconds since Unix epoch)
    epoch_unix_vals = (df.index.astype(int) // 10**9).astype(np.int32)

    # Explicitly create variable as CDF_INT4 (code 32)
    cdf_data.new("Unix_time", data=epoch_unix_vals)
    # Set internal fill value
    # cdf_data["Unix_time"].pad = np.int32(-2147483648)
    cdf_data["Unix_time"].attrs.update(
        {
            "FIELDNAM": "Time in Unix Epoch",
            "VALIDMIN": np.int32(epoch_unix_vals.min()),
            "VALIDMAX": np.int32(epoch_unix_vals.max()),
            "SCALEMIN": np.int32(epoch_unix_vals.min()),
            "SCALEMAX": np.int32(epoch_unix_vals.max()),
            "LABLAXIS": "Unix Time",
            "UNITS": "s",
            "MONOTON": "INCREASE",
            "VAR_TYPE": "support_data",
            "FORMAT": "I10",
            "FILLVAL": np.int32(-2147483648),  # standard ISTP fill value for INT4
            "DEPEND_0": "Epoch",
            "DICT_KEY": "time>Unix_time",
            "CATDESC": "Time, centered, in Unix Epoch seconds",
            "AVG_TYPE": " ",
            "DISPLAY_TYPE": " ",
            "VAR_NOTES": " ",
        }
    )
    photon_vars = [
        "photon_x_mcp",
        "photon_y_mcp",
        "photon_RA",
        "photon_Dec",
        "photon_az",
        "photon_el",
    ]

    eph_vars = [
        # "lexi_sc_eph_epoch",
        "lexi_sc_pos_gse_x",
        "lexi_sc_pos_gse_y",
        "lexi_sc_pos_gse_z",
        "sza",
    ]

    var_list = photon_vars + eph_vars

    for var in var_list:
        if var in df.columns:
            cdf_data[var] = df[var].values
            print(f"Added variable: {var}")
        elif var in df_eph.columns:
            cdf_data[var] = df_eph[var].values
            print(f"Added variable: {var}")

    # Copy variable attributes from skeleton
    for varname in skeleton_cdf:
        if varname in cdf_data:
            for attr in skeleton_cdf[varname].attrs:
                try:
                    cdf_data[varname].attrs[attr] = skeleton_cdf[varname].attrs[attr][...]
                except Exception:
                    cdf_data[varname].attrs[attr] = skeleton_cdf[varname].attrs[attr]

    skeleton_cdf.close()
    cdf_data.close()

    # Copy the output CDF to the SPDF directory
    # spdf_data_dir = Path(
    #     "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l1c/"
    # )
    # spdf_data_dir.mkdir(parents=True, exist_ok=True)
    # shutil.copy(cdf_file, spdf_data_dir / cdf_file.name)

    return str(cdf_file)
