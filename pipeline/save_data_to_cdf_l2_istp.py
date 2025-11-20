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
    logical_source: str = "clps-bgm1_lexi_l2-images",
    version: int = 0,
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
        Version string in the form '0'.
    output_dir : Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Full path to the generated filename.
    """
    start_str = start_time.strftime("%Y%m%d%H%M")
    while True:
        version_str = f"V{version}"
        # print(f"Current version: {version}, type {type(version)} {version_str}")
        filename = f"{logical_source}_{start_str}_{version_str}.cdf"
        file_path = output_dir / filename

        if not file_path.exists():
            break

        # print(f"File {filename} exists. Incrementing version.")
        # Update version
        version += 1

    # print(f"Generated CDF filename: {filename} in {output_dir}")
    return output_dir / filename


def save_data_to_cdf(
    data: dict = None,
    output_dir: Optional[StrPath] = None,
    version: int = 0,
    logical_source: str = "clps-bgm1_lexi_l2-images",
):
    """
    Save data to an ISTP-compliant LEXI CDF file.

    Parameters
    ----------
    data : dict
        Dictionary containing data arrays and metadata.
    output_dir : StrPath, optional
        Directory to save the CDF file. Defaults to current directory.
    version : int
        Version number as an integer.
    logical_source : str
        Logical source name, e.g., 'clps-bgm1_lexi_l2-images'.

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
        "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l2/clps-bgm1_lexi_l2-images_000000000000_v02.cdf"
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
        "az_bin",
        "el_bin",
        "az_bin_map",
        "el_bin_map",
        "pixel_area",
        "exposure_map",
        "flat_field_map",
        "cosmic_background_map",
        "dark_background_map",
        "total_background_map",
        "lexi_image",
        "lexi_image_background_corrected",
        "lexi_image_background_flatfield_corrected",
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
    # Copy the cdf file to
    # "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l2/"
    # shutil.copy(
    #     cdf_file,
    #     "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/spdf_data_documents/l2/",
    # )
    return cdf_file
