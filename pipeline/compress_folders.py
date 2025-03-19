import os
import shutil
from pathlib import Path


def compress_subfolders(folder_name):
    """
    Compresses all subfolders inside the given folder into separate ZIP files.

    Parameters
    ----------
    folder_name : str
        Path to the folder containing subfolders to compress.
    """
    # Convert folder_name to a Path object
    folder_path = Path(folder_name)

    # Check if the folder exists
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: The folder '{folder_name}' does not exist or is not a directory.")
        return

    # Iterate over all subfolders in the folder
    for subfolder in folder_path.iterdir():
        if subfolder.is_dir():
            # Create a ZIP file name based on the subfolder name
            zip_file_name = folder_path / f"{subfolder.name}.zip"

            # Compress the subfolder into a ZIP file
            print(f"Compressing '{subfolder.name}' into '{zip_file_name}'...")
            shutil.make_archive(str(zip_file_name.with_suffix("")), "zip", subfolder)

    print("Compression completed!")


# Example usage
folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1a/hk/csv/"
compress_subfolders(folder_name)
