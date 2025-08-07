import datetime
import shutil
import warnings
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from spacepy.pycdf import CDF as cdf

# Suppress warnings
warnings.filterwarnings("ignore")

StrPath = Union[str, Path]


def generate_lexi_cdf_filename(
    start_time: datetime.datetime,
    logical_source: str = "lexi_l1c",
    version: str = "0.1",
    output_dir: Path = Path("."),
) -> Path:
    """
    Generate an ISTP-compliant LEXI CDF filename.

    Parameters
    ----------
    start_time : datetime
        Start time of the data (in UTC).
    logical_source : str
        Logical source name, e.g., 'lexi_l1c'.
    version : str
        Version string in the form '0.1'.
    output_dir : Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Full path to the generated filename.
    """
    start_str = start_time.strftime("%Y%m%d%H")
    # Extract initial version parts
    primary_version = int(version.split(".")[0])
    secondary_version = int(version.split(".")[1])

    while True:
        version_str = f"V{primary_version}.{secondary_version}"
        filename = f"{logical_source}_{start_str}_{version_str}.cdf"
        file_path = output_dir / filename

        if not file_path.exists():
            break

        # Update version: bump secondary version (or whatever logic you prefer)
        secondary_version += 1
        if secondary_version > 9:
            secondary_version = 0
            primary_version += 1

    print(f"Generated CDF filename: {filename} in {output_dir}")
    return output_dir / filename


def save_data_to_cdf(
    df: Optional[pd.DataFrame] = None,
    output_dir: Optional[StrPath] = None,
    version: str = "0.0",
    logical_source: str = "lexi_l1c",
):
    """
    Save a DataFrame to a CDF file using a skeleton ISTP-compliant CDF file.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with datetime index and photon data columns.
    output_dir : str or Path
        Folder where the CDF file will be saved.
    version : str
        Semantic version number, e.g., "0.1".
    logical_source : str
        Logical source name (default: "lexi_l1c").

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

    cdf_file = generate_lexi_cdf_filename(
        start_time=start_time,
        logical_source=logical_source,
        version=version,
        output_dir=output_dir,
    )

    # Path to the read-only skeleton
    skeleton_path = Path(
        "/projectnb/sw-prop/qudsira/bu_research/lexi_data_run/data/skeleton_file/lexi_l1c_0000000000_v0.1.cdf"
    )

    # Load the skeleton in read-only mode
    skeleton_cdf = cdf(str(skeleton_path))

    # Create new writable CDF file (overwrite if exists)
    # if cdf_file.exists():
    #     cdf_file.unlink()
    cdf_data = cdf(str(cdf_file), "")

    # Copy global attributes from skeleton
    for key in skeleton_cdf.attrs:
        cdf_data.attrs[key] = skeleton_cdf.attrs[key][...]

    # Update dynamic global attributes
    cdf_data.attrs.update(
        {
            "Generation_date": str(datetime.datetime.now(datetime.timezone.utc)),
            "Logical_file_id": cdf_file.stem,
            "source": cdf_file.name,
        }
    )
    # ========== Variables ==========
    cdf_data["Epoch"] = df.index

    # Convert index to signed 32-bit integers (seconds since Unix epoch)
    epoch_unix_vals = (df.index.astype(int) // 10**9).astype(np.int32)

    # Explicitly create variable as CDF_INT4 (code 32)
    cdf_data.new("Epoch_unix", data=epoch_unix_vals)
    # Set internal fill value
    # cdf_data["Epoch_unix"].pad = np.int32(-2147483648)
    cdf_data["Epoch_unix"].attrs.update(
        {
            "FIELDNAM": "Time in Unix Epoch",
            "VALIDMIN": np.int32(epoch_unix_vals.min()),
            "VALIDMAX": np.int32(epoch_unix_vals.max()),
            "SCALEMIN": np.int32(epoch_unix_vals.min()),
            "SCALEMAX": np.int32(epoch_unix_vals.max()),
            "LABLAXIS": "Epoch Unix",
            "UNITS": "s",
            "MONOTON": "INCREASE",
            "VAR_TYPE": "support_data",
            "FORMAT": "I10",
            "FILLVAL": np.int32(-2147483648),  # standard ISTP fill value for INT4
            "DEPEND_0": "Epoch",
            "DICT_KEY": "time>Epoch_unix",
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

    for var in photon_vars:
        if var in df.columns:
            # Let data type match the skeleton — no need to force type
            cdf_data[var] = df[var].values

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
