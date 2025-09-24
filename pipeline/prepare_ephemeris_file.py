import datetime
import getpass

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

# Check the username to set file paths
user = getpass.getuser()

lexi_file_name = f"/home/{user}/Desktop/git/Lexi-Bu/lexi_data_pipeline/data/ephemeris_data/LEXIAngleData_ACTUAL_20250723.csv"

lunar_file_name = f"/home/{user}/Desktop/git/Lexi-Bu/lexi_data_pipeline/data/ephemeris_data/LEXI_Lunar_Pos_cleaned.txt"

df_eph = pd.read_csv(lexi_file_name)
# Rename "[Epoch (UTC)]" to "Epoch"
df_eph.rename(columns={"[Epoch (UTC)]": "Epoch"}, inplace=True)
# Convert Epoch from Mar 02 2025 09:34:00.00000000 to datetime format
df_eph["Epoch"] = pd.to_datetime(df_eph["Epoch"], format="%b %d %Y %H:%M:%S.%f")
# Set the index to be the Epoch column
df_eph.set_index("Epoch", inplace=True)

columns_to_rename = {
    "[E2L GSE x (km)]": "lexi_sc_pos_gse_x",
    "[E2L GSE y (km)]": "lexi_sc_pos_gse_y",
    "[E2L GSE z (km)]": "lexi_sc_pos_gse_z",
    "[SZA (deg)]": "sza",
}
df_eph.rename(columns=columns_to_rename, inplace=True)

# Drop the columns that are not needed
columns_to_keep = list(columns_to_rename.values())
df_eph = df_eph[columns_to_keep]

# Modify the data to have 10 minute intervals
# df_eph = df_eph.resample("10T").interpolate(method="linear")

df = df_eph.copy()
df.index = pd.to_datetime(df.index, utc=True)

# Target grid
idx10 = pd.date_range(df.index.min(), df.index.max(), freq="10min", tz=df.index.tz)

df_10m_linear = df.reindex(idx10).interpolate(method="time")

# Save the index as a column (named lexi_sc_eph_epoch)
df_10m_linear["lexi_sc_eph_epoch"] = df_10m_linear.index

# print(df_eph.head())
# print(df_10m_linear.head())

# Read the lunar position data
df_lunar = pd.read_csv(
    lunar_file_name,
    sep=r"\s+",
    engine="python",
    dtype={"Date": str, "Time": str, "X": float, "Y": float, "Z": float},
)

# Rename X, Y, Z to moon_pos_gse_x, moon_pos_gse_y, moon_pos_gse_z
df_lunar.rename(
    columns={"X": "moon_pos_gse_x", "Y": "moon_pos_gse_y", "Z": "moon_pos_gse_z"},
    inplace=True,
)
epoch = pd.to_datetime(
    df_lunar["Date"] + " " + df_lunar["Time"],
    format="%y/%m/%d %H:%M:%S",
    utc=True,
    errors="raise",
)

out = df_lunar.drop(columns=["Date", "Time"]).copy()
out.insert(0, "Epoch", epoch)

out.set_index("Epoch", inplace=True)

# Modify the data to have 10 minute intervals
out.index = pd.to_datetime(out.index)
idx10 = pd.date_range(out.index.min(), out.index.max(), freq="10min", tz=out.index.tz)
out_10m_linear = out.reindex(idx10).interpolate(method="time")

# Merge the lunar data with the ephemeris data using mergeasof
df_10m_linear = pd.merge_asof(
    df_10m_linear.sort_index(),
    out_10m_linear.sort_index(),
    left_index=True,
    right_index=True,
    direction="backward",
)

# Combine the Date and Time columns into a single datetime column (date is in the format of )
# Save to CSV
interpolated_file = lexi_file_name.replace(".csv", "_10min_linear.csv")
df_10m_linear.to_csv(interpolated_file, index_label="Epoch")
print(f"Saved 10-minute linear interpolated ephemeris to {interpolated_file}")

show_figure = False
if show_figure:
    # Plot the data
    fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    date_form = DateFormatter("%Y-%m-%d\n%H:%M:%S")
    axs[0].plot(df.index, df["lexi_sc_pos_gse_x"], label="Original", color="blue", alpha=0.5)
    axs[0].plot(
        df_10m_linear.index,
        df_10m_linear["lexi_sc_pos_gse_x"],
        label="10-min Linear Interpolated",
        color="red",
        linestyle="--",
    )
    axs[0].set_ylabel("LEXI X (km)")
    axs[0].legend()
    axs[0].grid()
    axs[0].xaxis.set_major_formatter(date_form)
    axs[0].set_title("LEXI Ephemeris Data with 10-minute Linear Interpolation")
    axs[1].plot(df.index, df["lexi_sc_pos_gse_y"], label="Original", color="blue", alpha=0.5)
    axs[1].plot(
        df_10m_linear.index,
        df_10m_linear["lexi_sc_pos_gse_y"],
        label="10-min Linear Interpolated",
        color="red",
        linestyle="--",
    )
    axs[1].set_ylabel("LEXI Y (km)")
    axs[1].legend()
    axs[1].grid()
    axs[1].xaxis.set_major_formatter(date_form)
    axs[2].plot(df.index, df["lexi_sc_pos_gse_z"], label="Original", color="blue", alpha=0.5)
    axs[2].plot(
        df_10m_linear.index,
        df_10m_linear["lexi_sc_pos_gse_z"],
        label="10-min Linear Interpolated",
        color="red",
        linestyle="--",
    )
    axs[2].set_ylabel("LEXI Z (km)")
    axs[2].legend()
    axs[2].grid()
    axs[2].xaxis.set_major_formatter(date_form)
    axs[3].plot(df.index, df["sza"], label="Original", color="blue", alpha=0.5)
    axs[3].plot(
        df_10m_linear.index,
        df_10m_linear["sza"],
        label="10-min Linear Interpolated",
        color="red",
        linestyle="--",
    )
    axs[3].set_ylabel("SZA (deg)")
    axs[3].set_xlabel("Time (UTC)")
    axs[3].legend()
    axs[3].grid()
    axs[3].xaxis.set_major_formatter(date_form)
    plt.tight_layout()
    # plt.savefig("lexi_ephemeris_10min_interpolated.png", dpi=150)
    plt.show()
