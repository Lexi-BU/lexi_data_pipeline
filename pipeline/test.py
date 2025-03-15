import datetime
import glob
import importlib
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import save_data_to_cdf as sdtc

importlib.reload(sdtc)


sdtc.save_data_to_cdf(
    df=combined_df,
    file_name=output_hk_file_name,
    file_version=f"{primary_version}.{secondary_version}",
)
