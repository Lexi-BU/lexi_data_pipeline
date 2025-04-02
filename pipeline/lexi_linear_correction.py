import datetime
import glob
import importlib
from pathlib import Path

import l1b_processing_sci as gl1b
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dateutil import parser

importlib.reload(gl1b)

# define the main folder
for ii in range(2, 3):
    read_new_file = True
    if read_new_file:
        folder = Path(
            "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/pin_hole_testing_data_L1a/sci"
        )

        # get all csv files in the folder
        file_list = sorted(glob.glob(str(folder) + "/*.csv", recursive=True))

        file_number_to_read = ii
        voltage_list = [1987, 2150, 1900, 1800]
        # read the first file
        df = pd.read_csv(file_list[file_number_to_read])
        # Selecte only rows where IsCommanded is False
        df = df[df["IsCommanded"] == False]

        # Drop the IsCommanded column and Timestamp column
        # df.drop(columns=["IsCommanded", "TimeStamp"], inplace=True)

        # Set the date as index and set it to utc
        df["Date"] = df["Date"].apply(parser.parse)
        df["Date"] = df["Date"].dt.tz_convert("UTC")
        df.set_index("Date", inplace=True)

    df_l1b = gl1b.level1b_data_processing(df=df)

    # In a table, print the min, max, median, mean and standard deviation
    columns = [
        "Channel1",
        "Channel2",
        "Channel3",
        "Channel4",
        "Channel1_shifted",
        "Channel2_shifted",
        "Channel3_shifted",
        "Channel4_shifted",
        "x_volt",
        "y_volt",
        "x_volt_lin",
        "y_volt_lin",
        "x_mcp",
        "y_mcp",
        "x_mcp_nln",
        "y_mcp_nln",
    ]
    # Save the table as a csv file (3 significant digits)
    df_l1b[columns].describe().T.round(3).to_csv("../data/l1b_data_summary.csv")

    # Define the row number for each row
    row_num = np.array([4, 3, 2, 1, 0, -1, -2, -3, -4])

    # Define the number of holes in each of the nine rows
    num_holes = np.array([1, 5, 7, 7, 9, 7, 7, 5, 1])

    # Define the distance between adjacent holes in each of the nine rows
    dist_h_inch = 0.394
    dist_h_cm = dist_h_inch * 2.54

    # Define the distance from x-axis to the center of the first hole in each of the nine rows
    dist_x_cm = row_num * dist_h_cm

    # Define the diameter of the holes
    d_h_inch = 0.020
    d_h_cm = d_h_inch * 2.54

    # Define the x and y coordinates of each of the holes
    x_holes = np.array([])
    y_holes = np.array([])
    for i in range(0, len(row_num)):
        hole_number = np.arange(-(num_holes[i] - 1) / 2, (num_holes[i] - 1) / 2 + 1, 1)
        y_holes = np.append(y_holes, dist_x_cm[i] * np.ones(len(hole_number)))
        x_holes = np.append(x_holes, hole_number * dist_h_cm)

    # Add the location of four more holes separately
    x_holes = np.append(x_holes, np.array([-0.197, 0.197, 0.984, -0.197]) * 2.54)
    y_holes = np.append(y_holes, np.array([-0.591, -0.197, 0.197, 1.378]) * 2.54)
    xy_holes = np.array([x_holes, y_holes])

    # Define a new coordinate system where the previous coordinate system is rotated by 45 degrees
    if "1900" in file_list[file_number_to_read]:
        theta = np.radians(-44.5)
    elif "2100" in file_list[file_number_to_read]:
        theta = np.radians(-90)
    theta_deg = np.degrees(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.array(((c, -s), (s, c)))
    xy_new_holes = np.dot(R, xy_holes)

    x_key_list = [
        "x_mcp",
        # "x_mcp_nln",
    ]  # "x_mcp", "x_mcp_nln"]  # , "x_volt_lin", "x_cm"]
    y_key_list = [
        "y_mcp",
        # "y_mcp_nln",
    ]  # "y_mcp", "y_mcp_nln"]  # , "y_volt_lin", "y_cm"]
    # Make histogram
    for histogram_x_key, histogram_y_key in zip(x_key_list, y_key_list):
        input_data = {
            "df": df_l1b,
            "lower_threshold": 1,
            "upper_threshold": 4.51,
            "sum_lower_threshold": 8,
            "sum_upper_threshold": 12,
            "histogram_x_key": histogram_x_key,
            "histogram_y_key": histogram_y_key,
            "bins": 300,
            "min_count": 5,
            "holes_data": xy_new_holes,
            "save_fig": True,
            "file_name": file_list[file_number_to_read],
        }
        fig_name = f"thresholded_histogram_{input_data['histogram_x_key']}_vs_{input_data['histogram_y_key']}_{file_number_to_read}_{voltage_list[ii]}V.png"
        fig, ax = gl1b.make_thresholded_histogram(**input_data, fig_name=fig_name)
        plt.close(fig)
