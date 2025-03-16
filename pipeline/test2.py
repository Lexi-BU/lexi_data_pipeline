import glob
import re
from datetime import datetime

from dateutil import parser

data_folder_location = "/mnt/cephadrius/bu_research/lexi_data/L1b/sci/cdf/"

start_time = "2025-01-16T00:00:00.00Z"
end_time = "2025-01-16T23:59:59.00Z"

start_time = parser.parse(start_time)
end_time = parser.parse(end_time)


def get_file_list(folder_name, start_time, end_time):
    # Construct the folder path
    folder_name = data_folder_location + start_time.strftime("%Y-%m-%d")

    # Get all .cdf files recursively
    file_list = sorted(glob.glob(folder_name + "/**/*.cdf", recursive=True))

    # Regex pattern to extract timestamps from filenames
    pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})"
    )

    filtered_files = []
    for file in file_list:
        match = pattern.search(file)
        if match:
            start_dt_str = match.group(1) + "T" + match.group(2).replace("-", ":") + "Z"
            end_dt_str = match.group(3) + "T" + match.group(4).replace("-", ":") + "Z"
            print(f"Start datetime string: {start_dt_str}")
            print(f"End datetime string: {end_dt_str}")
            file_start_time = parser.parse(start_dt_str)
            file_end_time = parser.parse(end_dt_str)

            # Check if the file is within the time range
            if file_start_time <= end_time and file_end_time >= start_time:
                filtered_files.append(file)

    return filtered_files

