import importlib
import sys
from pathlib import Path

import get_l2_files as gl2f

sys.path.append("../../lexi_data_analysis/data_analysis")

import lexi_data_analysis_functions_istp as ldaf

importlib.reload(ldaf)
importlib.reload(gl2f)

# Read all data files in a given time range
# NOTE: Make sure to set the correct time range and data folder location.
read_data = False
if read_data:
    df = ldaf.read_all_data_files(
        file_list=None,
        start_time="2025-03-16 18:00",
        end_time="2025-03-16 19:05",
        return_data_type="dataframe",
        kwargs={
            "data_folder_location": "/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf",
            "version": "latest",
            "start_time": "2025-03-16 18:00",
            "end_time": "2025-03-16 19:55",
        },
    )


# Suppose you already extracted arrays from your L1c CDF:
# t_unix: seconds (e.g., via cdflib epochs_to_unix)
# ra_deg: from "photon_RA"
# dec_deg: from "photon_Dec"
out = gl2f.df_to_hist2d_fits(
    df,
    x_col="photon_az",
    y_col="photon_el",
    bin_minutes=5,
    x_range=(260, 280),
    y_range=(16, 36),
    x_bins=100,
    y_bins=100,
    as_rate=False,
    filename="lexi_l2_az_el_5min_counts.fits",
)
print("Wrote:", out)
