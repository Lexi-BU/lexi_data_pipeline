import datetime
import glob
import importlib
import re
import warnings
from pathlib import Path

import get_l1c_files_sci_parallel as gl1c
import numpy as np
import pandas as pd
import save_data_to_cdf as sdtc
from dateutil import parser
from tqdm import tqdm  # Import tqdm for the progress bar

importlib.reload(sdtc)
importlib.reload(gl1c)


sci_folder = "/home/cephadrius/Downloads/"

file_val_list = sorted(glob.glob(str(sci_folder) + "/**/*.cdf", recursive=True))

start_time = "2025-03-16T19:00:00Z"
end_time = "2025-03-16T19:59:59Z"

start_time = parser.parse(start_time)
end_time = parser.parse(end_time)

file_val_list = [
    file
    for file in file_val_list
    if (
        (match := re.search(r"payload_lexi_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", file))
        and start_time
        <= datetime.datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S").replace(
            tzinfo=datetime.timezone.utc
        )
        <= end_time
    )
]
