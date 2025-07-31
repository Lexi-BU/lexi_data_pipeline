import datetime
import shutil
import warnings
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from spacepy.pycdf import CDF as cdf

# Suppress warnings
warnings.filterwarnings("ignore")

StrPath = Union[str, Path]


def generate_lexi_cdf_filename(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    descriptor: str = "l1c",
    logical_source: str = "clps_bgm1_mn_lexi",
    version: str = "0.1.0",
    output_dir: Path = Path("."),
) -> Path:
    """
    Generate an ISTP-compliant LEXI CDF filename.

    Parameters
    ----------
    start_time : datetime
        Start time of the data (in UTC).
    end_time : datetime
        End time of the data (in UTC).
    descriptor : str
        Data product descriptor, e.g., 'l1c'.
    logical_source : str
        Logical source name, e.g., 'clps_bgm1_mn_lexi'.
    version : str
        Version string in the form '0.1.0'.
    output_dir : Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Full path to the generated filename.
    """
    start_str = start_time.strftime("%Y%m%d%H%M")
    # end_str = end_time.strftime("%Y%m%d_%H%M%S")
    version_str = f"V{version}"
    filename = f"{logical_source}_{descriptor}_{start_str}_{version_str}.cdf"
    print(f"Generated CDF filename: {filename} in {output_dir}")
    return output_dir / filename


def save_data_to_cdf(
    df: Optional[pd.DataFrame] = None,
    output_dir: Optional[StrPath] = None,
    version: str = "0.1.0",
    descriptor: str = "l1c",
    logical_source: str = "clps_bgm1_mn_lexi",
):
    """
    Save a DataFrame to a CDF file in an ISTP-compliant format with auto-generated filename.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with datetime index and photon data columns.
    output_dir : str or Path
        Folder where the CDF file will be saved.
    version : str
        Semantic version number, e.g., "0.1.0".
    descriptor : str
        Data product descriptor (default: "l1c").
    logical_source : str
        Logical source name (default: "clps_bgm1_mn_lexi").

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
    end_time = df.index[-1].to_pydatetime()

    cdf_file = generate_lexi_cdf_filename(
        start_time=start_time,
        end_time=end_time,
        descriptor=descriptor,
        logical_source=logical_source,
        version=version,
        output_dir=output_dir,
    )

    if cdf_file.exists():
        cdf_file.unlink()

    print(f"Saving data to CDF file: {cdf_file.name}")
    print(f"Output directory: {output_dir}")

    cdf_data = cdf(str(cdf_file), "")

    # ========== Global Attributes ==========
    cdf_data.attrs.update(
        {
            "TITLE": cdf_file.stem,
            "created": str(datetime.datetime.now(datetime.timezone.utc)),
            "TimeZone": "UTC",
            "creator": "Ramiz A. Qudsi",
            "source": cdf_file.name,
            "source_type": "csv",
            "source_format": "lxi",
            "source_version": version,
            "source_description": "X-ray data from the LEXI spacecraft",
            "source_description_url": "https://lexi-bu.github.io/",
            "source_description_email": "leximoon@bu.edu",
            "source_description_institution": "Boston_University",
            # ISTP-required attributes
            "Logical_file_id": cdf_file.stem,
            "Project": "LEXI",
            "Source_name": "LEXI",
            "Descriptor": descriptor,
            "Data_type": descriptor,
            "Discipline": "Space Physics>Heliophysics",
            "PI_name": "Brian Walsh",
            "PI_affiliation": "Boston University",
            "TEXT": "LEXI photon hit event data",
            "Mission_group": "NASA",
            "Instrument_type": "Imagers (space)",
            "Logical_source": logical_source,
            "Logical_source_description": "LEXI Level-1c data from MCP events",
        }
    )

    # ========== Variables ==========
    cdf_data["Epoch"] = df.index
    cdf_data["Epoch"].attrs.update(
        {
            "TIME_BASE": "J2000",
            "FORMAT": "yyyy-mm-ddThh:mm:ss.sssZ",
            "Description": "The epoch time in UTC.",
            "UNITS": "Seconds since 1970-01-01T00:00:00Z",
            "VAR_TYPE": "support_data",
            "FIELDNAM": "Epoch",
            "CATDESC": "Timestamp of each event in UTC",
            "FILLVAL": "NaT",
            "VALIDMIN": df.index.min().to_pydatetime(),
            "VALIDMAX": df.index.max().to_pydatetime(),
            "LABLAXIS": "Time",
        }
    )

    cdf_data["Epoch_unix"] = df.index.astype(int) // 10**9
    cdf_data["Epoch_unix"].attrs.update(
        {
            "FORMAT": "T",
            "Description": "The epoch time in Unix format.",
            "UNITS": "Seconds since 1970-01-01T00:00:00Z",
            "VAR_TYPE": "support_data",
            "DEPEND_0": "Epoch",
            "FIELDNAM": "Epoch_unix",
            "CATDESC": "Unix timestamp (seconds since 1970-01-01)",
            "FILLVAL": -1,
            "VALIDMIN": int(df.index.min().timestamp()),
            "VALIDMAX": int(df.index.max().timestamp()),
            "LABLAXIS": "UnixTime",
        }
    )

    for col in [
        "photon_x_mcp",
        "photon_y_mcp",
        "photon_RA",
        "photon_Dec",
        "photon_az",
        "photon_el",
    ]:
        if col in df.columns:
            description = {
                "photon_x_mcp": "The value of the x-axis in mcp coordinates.",
                "photon_y_mcp": "The value of the y-axis in mcp coordinates.",
                "photon_RA": "The right ascension of the photon in degrees.",
                "photon_Dec": "The declination of the photon in degrees.",
                "photon_az": "The azimuthal angle of the photon in degrees in the local topocentric frame. The angle is measured from the north direction.",
                "photon_el": "The elevation angle of the photon in degrees in the local topocentric frame. The angle is measured from the horizontal plane.",
            }[col]

            units = {
                "photon_x_mcp": "Centimeters",
                "photon_y_mcp": "Centimeters",
                "photon_RA": "Degrees",
                "photon_Dec": "Degrees",
                "photon_az": "Degrees",
                "photon_el": "Degrees",
            }[col]

            cdf_data[col] = df[col].values
            cdf_data[col].attrs.update(
                {
                    "Description": description,
                    "UNITS": units,
                    "VAR_TYPE": "data",
                }
            )

    # Data variables
    for var in [
        "photon_x_mcp",
        "photon_y_mcp",
        "photon_RA",
        "photon_Dec",
        "photon_az",
        "photon_el",
    ]:
        cdf_data[var].attrs.update(
            {
                "VAR_TYPE": "data",
                "DISPLAY_TYPE": "time_series",
                "DEPEND_0": "Epoch",
                "FIELDNAM": var,
                "CATDESC": var.replace("_", " ").title(),
                "LABLAXIS": var.split("_")[1].upper(),
                "FORMAT": "F10.3",
                "FILLVAL": -1.0e31,
                "VALIDMIN": df[var].min(),
                "VALIDMAX": df[var].max(),
            }
        )
    cdf_data.close()

    # Using pathlib, copy the cdf file to this directory:
    # /home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l1c/
    spdf_data_dir = Path(
        "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l1c/"
    )
    spdf_data_dir.mkdir(parents=True, exist_ok=True)
    # copy the cdf file to the spdf_data_dir using shutil
    shutil.copy(cdf_file, spdf_data_dir / cdf_file.name)
    return str(cdf_file)
