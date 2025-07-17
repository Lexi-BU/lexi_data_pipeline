import glob
from pathlib import Path

import pandas as pd
from spacepy.pycdf import CDF as cdf

# Define the folder containing the CDF files
folder_name = "/mnt/cephadrius/bu_research/lexi_data/L1c/sci/cdf/2025-03-16/"

# Get the list of CDF files in the folder and subfolders
file_val_list = sorted(glob.glob(str(folder_name) + "/**/*v0.0.cdf", recursive=True))

df_list = []
selected_columns = [
    "Epoch",
    "photon_x_mcp",
    "photon_y_mcp",
    "photon_RA",
    "photon_Dec",
    "photon_az",
    "photon_el",
]
for file_val in file_val_list:
    print(f"Reading file: {file_val} of {len(file_val_list)}")
    dat = cdf(file_val)
    dft = pd.DataFrame({key: dat[key][:] for key in selected_columns})
    # Convert the CDF data to a DataFrame
    df_list.append(dft)

# Concatenate all DataFrames into a single DataFrame
df = pd.concat(df_list, ignore_index=True)
# Convert the Epoch column to datetime
df["Epoch"] = pd.to_datetime(df["Epoch"], unit="s", utc=True)
# Set the Epoch column as the index
df.set_index("Epoch", inplace=True)

# Resample to 1-second intervals and count the number of data points
df["Epoch"] = df.index
df["Epoch_seconds"] = df["Epoch"].dt.ceil("S")
counts_per_second = df.groupby("Epoch_seconds").size()
# Save the counts to a CSV file
output_csv_file = Path("../data/counts_per_second.csv")
output_csv_file.parent.mkdir(parents=True, exist_ok=True)
counts_per_second.to_csv(output_csv_file)
print(f"Counts per second saved to {output_csv_file}")
