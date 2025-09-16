import datetime
import shutil
import warnings
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from spacepy.pycdf import CDF as cdf
from spacepy.pycdf import const

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
    start_str = start_time.strftime("%Y%m%d%H%M")
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
    data: dict = None,
    output_dir: Optional[StrPath] = None,
    version: str = "0.0",
    logical_source: str = "lexi_l2",
):
    """
    Save data to an ISTP-compliant LEXI CDF file.

    Parameters
    ----------
    data : dict
        Dictionary containing data arrays and metadata.
    output_dir : StrPath, optional
        Directory to save the CDF file. Defaults to current directory.
    version : str
        Version string in the form '0.1'.
    logical_source : str
        Logical source name, e.g., 'lexi_l2'.

    Returns
    -------
    Path
        Path to the saved CDF file.
    """
    if data is None:
        raise ValueError("Data dictionary must be provided.")

    if output_dir is None:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    cdf_file = generate_lexi_cdf_filename(
        start_time=data["epoch_start"],
        logical_source=logical_source,
        version=version,
        output_dir=output_dir,
    )

    # Path to the read-only skeleton file
    skeleton_path = Path(
        "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l2/lexi_l2_000000000000_v0.2.cdf"
    )
    if not skeleton_path.exists():
        raise FileNotFoundError(f"Skeleton file not found: {skeleton_path}")

    # Load the skeleton in read-only mode
    skeleton_cdf = cdf(str(skeleton_path))

    # Create new writable CDF file
    cdf_data = cdf(str(cdf_file), str(skeleton_path))

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

    data_vars = [
        "epoch_start",
        "epoch_end",
        "ra_bin",
        "dec_bin",
        "ra_bin_map",
        "dec_bin_map",
        "exposure_map",
        "flat_field_map",
        "galactic_background_map",
        "dark_background_map",
        "total_background_map",
        "lexi_histogram",
        "lexi_histogram_background_corrected",
        "lexi_histogram_background_flatfield_corrected",
    ]

    for vname in data_vars:
        v = cdf_data[vname]
        arr = np.asarray(data[vname])
        if v.rv() and arr.ndim == len(v.shape) - 1:
            arr = arr[np.newaxis, ...]
        v[...] = arr

    print(f"Saved CDF file: {cdf_file}")
    skeleton_cdf.close()
    cdf_data.close()
    return cdf_file
