import importlib

import get_l1c_files_sci_parallel as gl1c
import pandas as pd
from spacepy.pycdf import CDF as cdf

importlib.reload(gl1c)

R_db = gl1c.get_body_detector_rotation_matrix(epoch_value="2025-03-16T19:00:00Z")
print(f"R_db: {R_db}")
