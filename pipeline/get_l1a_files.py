import csv
import datetime
import importlib
import os
import struct
from pathlib import Path
from typing import NamedTuple

import lxi_misc_codes as lmsc
import numpy as np
import pandas as pd
import pytz

lmsc = importlib.reload(lmsc)

# Get the user login name
user_name = os.getlogin()

level_zero_folder = f"/home/{user_name}/Desktop/git/Lexi-BU/lexi_data_pipeline/data/level_0/"

level_zero_folder = Path(level_zero_folder).expanduser().resolve()

# Tha packet format of the science and housekeeping packets
packet_format_sci = ">II4H"
# signed lower case, unsigned upper case (b)
packet_format_hk = ">II4H"

# double precision format for time stamp from pit
packet_format_pit = ">d"

sync_lxi = b"\xfe\x6b\x28\x40"

sync_pit = b"\x54\x53"

volts_per_count = 4.5126 / 65536  # volts per increment of digitization


class sci_packet_cls(NamedTuple):
    """
    Class for the science packet.
    The code unpacks the science packet into a named tuple. Based on the packet format, each packet
    is unpacked into following parameters:
    - Date: time of the packet as received from the PIT
    - timestamp: int (32 bit)
    - IsCommanded: bool (1 bit)
    - voltage channel1: float (16 bit)
    - voltage channel2: float (16 bit)
    - voltage channel3: float (16 bit)
    - voltage channel4: float (16 bit)

    TimeStamp is the time stamp of the packet in seconds.
    IsCommand tells you if the packet was commanded.
    Voltages 1 to 4 are the voltages of corresponding different channels.
    """

    Date: float
    is_commanded: bool
    timestamp: int
    channel1: float
    channel2: float
    channel3: float
    channel4: float

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        structure_time = struct.unpack(">d", bytes_[2:10])
        structure = struct.unpack(packet_format_sci, bytes_[12:])
        if structure[1] & 0x80000000:
            return
        else:
            return cls(
                Date=structure_time[0],
                is_commanded=bool(
                    structure[1] & 0x40000000
                ),  # mask to test for commanded event type
                timestamp=structure[1] & 0x3FFFFFFF,  # mask for getting all timestamp bits
                channel1=structure[2] * volts_per_count,
                channel2=structure[3] * volts_per_count,
                channel3=structure[4] * volts_per_count,
                channel4=structure[5] * volts_per_count,
            )


class hk_packet_cls(NamedTuple):
    """
    Class for the housekeeping packet.
    The code unpacks the HK packet into a named tuple. Based on the document and data structure,
    each packet is unpacked into
    - Date: time of the packet as received from the PIT
    - "timestamp",
    - "hk_id" (this tells us what "hk_value" stores inside it),
    - "hk_value",
    - "delta_event_count",
    - "delta_drop_event_count", and
    - "delta_lost_event_count".

    Based on the value of "hk_id", "hk_value" might correspond to value of following parameters:
    NOTE: "hk_id" is a number, and varies from 0 to 15.
    0: PinPuller Temperature
    1: Optics Temperature
    2: LEXI Base Temperature
    3: HV Supply Temperature
    4: Current Correspoding to the HV Supply (5.2V)
    5: Current Correspoding to the HV Supply (10V)
    6: Current Correspoding to the HV Supply (3.3V)
    7: Anode Voltage Monitor
    8: Current Correspoding to the HV Supply (28V)
    9: ADC Ground
    10: Command Count
    11: Pin Puller Armmed
    12: Unused
    13: Unused
    14: MCP HV after auto change
    15: MCP HV after manual change
    """

    Date: int
    timestamp: int
    hk_id: int
    hk_value: float
    delta_event_count: int
    delta_drop_event_count: int
    delta_lost_event_count: int

    @classmethod
    def from_bytes(cls, bytes_: bytes):
        structure_time = struct.unpack(">d", bytes_[2:10])
        structure = struct.unpack(packet_format_hk, bytes_[12:])
        # Check if the present packet is the house-keeping packet. Only the house-keeping packets
        # are processed.
        if structure[1] & 0x80000000:
            Date = structure_time[0]
            timestamp = structure[1] & 0x3FFFFFFF  # mask for getting all timestamp bits
            hk_id = (structure[2] & 0xF000) >> 12  # Down-shift 12 bits to get the hk_id
            if hk_id == 10 or hk_id == 11:
                hk_value = structure[2] & 0xFFF
            else:
                hk_value = (structure[2] & 0xFFF) << 4  # Up-shift 4 bits to get the hk_value
            delta_event_count = structure[3]
            delta_drop_event_count = structure[4]
            delta_lost_event_count = structure[5]

            return cls(
                Date=Date,
                timestamp=timestamp,
                hk_id=hk_id,
                hk_value=hk_value,
                delta_event_count=delta_event_count,
                delta_drop_event_count=delta_drop_event_count,
                delta_lost_event_count=delta_lost_event_count,
            )


def read_binary_data_sci(
    in_file_name=None,
    save_file_name="../data/processed/sci/output_sci.csv",
    number_of_decimals=6,
):
    """
    Reads science packet of the binary data from a file and saves it to a csv file.

    Parameters
    ----------
    in_file_name : str
        Name of the input file. Default is None.
    save_file_name : str
        Name of the output file. Default is "output_sci.csv".
    number_of_decimals : int
        Number of decimals to save. Default is 6.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist.
    TypeError :
        If the name of the input file or input directory is not a string. Or if the number of
        decimals is not an integer.
    Returns
    -------
        df : pandas.DataFrame
            DataFrame of the science packet.
        save_file_name : str
            Name of the output file.
    """
    if in_file_name is None:
        raise ValueError("The input file name must be provided.")

    # Check if the file exists, if does not exist raise an error
    if not Path(in_file_name).is_file():
        raise FileNotFoundError("The file " + in_file_name + " does not exist.")
    # Check if the file name and folder name are strings, if not then raise an error
    if not isinstance(in_file_name, str):
        raise TypeError("The file name must be a string.")

    # Check the number of decimals to save
    if not isinstance(number_of_decimals, int):
        raise TypeError("The number of decimals to save must be an integer.")

    input_file_name = in_file_name

    with open(input_file_name, "rb") as file:
        raw = file.read()

    index = 0
    packets = []

    while index < len(raw) - 28:
        if raw[index : index + 2] == sync_pit and raw[index + 12 : index + 16] == sync_lxi:
            packets.append(sci_packet_cls.from_bytes(raw[index : index + 28]))
            index += 28
            continue
        elif (raw[index : index + 2] == sync_pit) and (raw[index + 12 : index + 16] != sync_lxi):
            # Ignore the last packet
            if index >= len(raw) - 28 - 16:
                # NOTE: This is a temporary fix. The last packet is ignored because the last
                # packet often isn't complete. Need to find a better solution. Check the function
                # read_binary_data_hk for the same.
                index += 28
                continue
            # Check if sync_lxi is present in the next 16 bytes
            if sync_lxi in raw[index + 12 : index + 28] and index + 28 < len(raw):
                # Find the index of sync_lxi
                index_sync = index + 12 + raw[index + 12 : index + 28].index(sync_lxi)
                # Reorder the packet
                new_packet = (
                    raw[index + 28 : index + 12 + 28]
                    + raw[index_sync : index + 28]
                    + raw[index + 12 + 28 : index_sync + 28]
                )
                # Check if the packet length is 28
                if len(new_packet) != 28:
                    # If the index + 28 is greater than the length of the raw data, then break
                    if index + 28 > len(raw):
                        break
                packets.append(sci_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 3:index] + raw[index+12:index+13] == sync_lxi
            elif raw[index - 3 : index] + raw[index + 12 : index + 13] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 3 : index] + raw[index + 12 : index + 25]
                )
                packets.append(sci_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 2:index] + raw[index+12:index+14] == sync_lxi
            elif raw[index - 2 : index] + raw[index + 12 : index + 14] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 2 : index] + raw[index + 13 : index + 26]
                )
                packets.append(sci_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 1:index] + raw[index+12:index+15] == sync_lxi
            elif raw[index - 1 : index] + raw[index + 12 : index + 15] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 1 : index] + raw[index + 14 : index + 27]
                )
                packets.append(sci_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            index += 28
            continue
        index += 28

    # Drop the packets that are None
    packets = [packet for packet in packets if packet is not None]

    # Split the file name in a folder and a file name
    output_file_name = (
        os.path.basename(os.path.normpath(in_file_name)).split(".")[0] + "_sci_output_L1a.csv"
    )
    output_folder_name_list = os.path.dirname(os.path.normpath(in_file_name)).split("/")
    output_folder_name = (
        "/".join(output_folder_name_list[:-2]) + "/L1a/sci/" + output_folder_name_list[-1]
    )
    save_file_name = output_folder_name + "/" + output_file_name

    # Check if the save folder exists, if not then create it
    if not Path(output_folder_name).exists():
        Path(output_folder_name).mkdir(parents=True, exist_ok=True)

    with open(save_file_name, "w", newline="") as file:
        dict_writer = csv.DictWriter(
            file,
            fieldnames=(
                "Date",
                "TimeStamp",
                "IsCommanded",
                "Channel1",
                "Channel2",
                "Channel3",
                "Channel4",
            ),
        )
        dict_writer.writeheader()
        try:
            dict_writer.writerows(
                {
                    # "Date": datetime.datetime.utcfromtimestamp(sci_packet_cls.Date),
                    "Date": datetime.datetime.fromtimestamp(
                        sci_packet_cls.Date, tz=datetime.timezone.utc
                    ),
                    "TimeStamp": sci_packet_cls.timestamp / 1e3,
                    "IsCommanded": sci_packet_cls.is_commanded,
                    "Channel1": np.round(sci_packet_cls.channel1, decimals=number_of_decimals),
                    "Channel2": np.round(sci_packet_cls.channel2, decimals=number_of_decimals),
                    "Channel3": np.round(sci_packet_cls.channel3, decimals=number_of_decimals),
                    "Channel4": np.round(sci_packet_cls.channel4, decimals=number_of_decimals),
                }
                for sci_packet_cls in packets
            )
        except Exception as e:
            # Print the exception in red color
            print(f"\n\033[91m{e}\033[00m\n")
            print(
                f"Number of science packets found in the file \033[96m {in_file_name}\033[0m "
                f"is just \033[91m {len(packets)}\033[0m. \n \033[96m Check the datafile to "
                "see if the datafile has proper data.\033[0m \n "
            )

    # Read the saved file data in a dataframe
    df = pd.read_csv(save_file_name)

    # Convert the date column to datetime
    try:
        df["Date"] = pd.to_datetime(df["Date"])
    except Exception:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    except Exception:
        df["Date"] = pd.to_datetime(df["Date"], format="ISO8601")
    except Exception:
        # Use dateutil
        df["Date"] = pd.to_datetime(df["Date"], format=None, errors="coerce")

    # Set index to the date
    df.set_index("Date", inplace=False)

    # Save the dataframe to a csv file
    df.to_csv(save_file_name, index=False)

    return df, save_file_name


def read_binary_data_hk(
    in_file_name=None,
    save_file_name="../data/processed/hk/output_hk.csv",
    number_of_decimals=6,
):
    """
    Reads housekeeping packet of the binary data from a file and saves it to a csv file.

    Parameters
    ----------
    in_file_name : str
        Name of the input file. Default is None.
    save_file_name : str
        Name of the output file. Default is "output_hk.csv".
    number_of_decimals : int
        Number of decimals to save. Default is 6.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist.
    TypeError :
        If the name of the input file or input directory is not a string. Or if the number of
        decimals is not an integer.
    Returns
    -------
        df : pandas.DataFrame
            DataFrame of the housekeeping packet.
        save_file_name : str
            Name of the output file.

    Raises
    ------
    FileNotFoundError :
        If the input file does not exist or isn't a specified
    """
    if in_file_name is None:
        raise FileNotFoundError("The input file name must be specified.")

    # Check if the file exists, if does not exist raise an error
    if not Path(in_file_name).is_file():
        raise FileNotFoundError("The file " + in_file_name + " does not exist.")
    # Check if the file name and folder name are strings, if not then raise an error
    if not isinstance(in_file_name, str):
        raise TypeError("The file name must be a string.")

    # Check the number of decimals to save
    if not isinstance(number_of_decimals, int):
        raise TypeError("The number of decimals to save must be an integer.")

    input_file_name = in_file_name

    # print(f"Reading the file \033[96m {in_file_name}\033[0m")

    with open(input_file_name, "rb") as file:
        raw = file.read()

    index = 0
    packets = []
    # Get the packets from the raw data
    # Loop through the raw data and get the packets
    while index < len(raw) - 28:
        if raw[index : index + 2] == sync_pit and raw[index + 12 : index + 16] == sync_lxi:
            packets.append(hk_packet_cls.from_bytes(raw[index : index + 28]))
            index += 28
            continue
        elif raw[index : index + 2] == sync_pit and raw[index + 12 : index + 16] != sync_lxi:
            # Ignore the last packet
            if index >= len(raw) - 28 - 16:
                # NOTE: This is a temporary fix. The last packet is ignored because the last
                # packet often isn't complete. Need to find a better solution. Check the function
                # read_binary_data_sci for the same.
                index += 28
                continue
            # Check if sync_lxi is present in the next 16 bytes
            if sync_lxi in raw[index + 12 : index + 28] and index + 28 < len(raw):
                # Find the index of sync_lxi
                index_sync = index + 12 + raw[index + 12 : index + 28].index(sync_lxi)
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12]
                    + raw[index_sync : index + 28]
                    + raw[index + 12 + 28 : index_sync + 28]
                )
                # Check if the packet length is 28
                if len(new_packet) != 28:
                    # Print the packet length
                    print(
                        f"The packet length is {len(new_packet)}, index = {index} and length of raw is {len(raw)}"
                    )
                    print(f"{index} 1 ==> {new_packet.hex()}\n")
                    # If the index + 28 is greater than the length of the raw data, then break
                    if index + 28 > len(raw):
                        break
                packets.append(hk_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 3:index] + raw[index+12:index+13] == sync_lxi
            elif raw[index - 3 : index] + raw[index + 12 : index + 13] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 3 : index] + raw[index + 12 : index + 25]
                )
                packets.append(hk_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 2:index] + raw[index+12:index+14] == sync_lxi
            elif raw[index - 2 : index] + raw[index + 12 : index + 14] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 2 : index] + raw[index + 13 : index + 26]
                )
                packets.append(hk_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            # Check if raw[index - 1:index] + raw[index+12:index+15] == sync_lxi
            elif raw[index - 1 : index] + raw[index + 12 : index + 15] == sync_lxi:
                # Reorder the packet
                new_packet = (
                    raw[index : index + 12] + raw[index - 1 : index] + raw[index + 14 : index + 27]
                )
                packets.append(hk_packet_cls.from_bytes(new_packet))
                index += 28
                continue
            index += 28
            continue
        index += 28

    # Get only those packets that have the HK data
    hk_idx = []
    for idx, hk_packet in enumerate(packets):
        if hk_packet is not None:
            hk_idx.append(idx)

    Date = np.full(len(hk_idx), np.nan)
    TimeStamp = np.full(len(hk_idx), np.nan)
    HK_id = np.full(len(hk_idx), np.nan)
    PinPullerTemp = np.full(len(hk_idx), np.nan)
    OpticsTemp = np.full(len(hk_idx), np.nan)
    LEXIbaseTemp = np.full(len(hk_idx), np.nan)
    HVsupplyTemp = np.full(len(hk_idx), np.nan)
    V_Imon_5_2 = np.full(len(hk_idx), np.nan)
    V_Imon_10 = np.full(len(hk_idx), np.nan)
    V_Imon_3_3 = np.full(len(hk_idx), np.nan)
    AnodeVoltMon = np.full(len(hk_idx), np.nan)
    V_Imon_28 = np.full(len(hk_idx), np.nan)
    ADC_Ground = np.full(len(hk_idx), np.nan)
    Cmd_count = np.full(len(hk_idx), np.nan)
    Pinpuller_Armed = np.full(len(hk_idx), np.nan)
    Unused1 = np.full(len(hk_idx), np.nan)
    Unused2 = np.full(len(hk_idx), np.nan)
    HVmcpAuto = np.full(len(hk_idx), np.nan)
    HVmcpMan = np.full(len(hk_idx), np.nan)
    DeltaEvntCount = np.full(len(hk_idx), np.nan)
    DeltaDroppedCount = np.full(len(hk_idx), np.nan)
    DeltaLostEvntCount = np.full(len(hk_idx), np.nan)

    all_data_dict = {
        "Date": Date,
        "TimeStamp": TimeStamp,
        "HK_id": HK_id,
        "0": PinPullerTemp,
        "1": OpticsTemp,
        "2": LEXIbaseTemp,
        "3": HVsupplyTemp,
        "4": V_Imon_5_2,
        "5": V_Imon_10,
        "6": V_Imon_3_3,
        "7": AnodeVoltMon,
        "8": V_Imon_28,
        "9": ADC_Ground,
        "10": Cmd_count,
        "11": Pinpuller_Armed,
        "12": Unused1,
        "13": Unused2,
        "14": HVmcpAuto,
        "15": HVmcpMan,
        "DeltaEvntCount": DeltaEvntCount,
        "DeltaDroppedCount": DeltaDroppedCount,
        "DeltaLostEvntCount": DeltaLostEvntCount,
    }

    selected_keys = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
    ]

    for ii, idx in enumerate(hk_idx):
        hk_packet = packets[idx]
        # Convert to seconds from milliseconds for the timestamp
        if "payload" in in_file_name:
            all_data_dict["Date"][ii] = hk_packet.Date
        else:
            default_time = datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("UTC"))
            new_time = default_time + datetime.timedelta(milliseconds=hk_packet.timestamp)
            all_data_dict["Date"][ii] = new_time.timestamp()
        all_data_dict["TimeStamp"][ii] = hk_packet.timestamp / 1e3
        all_data_dict["HK_id"][ii] = hk_packet.hk_id
        key = str(hk_packet.hk_id)
        if key in selected_keys:
            all_data_dict[key][ii] = lmsc.hk_value_comp(
                ii=ii,
                vpc=volts_per_count,
                hk_value=hk_packet.hk_value,
                hk_id=hk_packet.hk_id,
                lxi_unit=1,
            )

        all_data_dict["DeltaEvntCount"][ii] = hk_packet.delta_event_count
        all_data_dict["DeltaDroppedCount"][ii] = hk_packet.delta_drop_event_count
        all_data_dict["DeltaLostEvntCount"][ii] = hk_packet.delta_lost_event_count

    # Create a dataframe with the data
    df_key_list = [
        "Date",
        "TimeStamp",
        "HK_id",
        "PinPullerTemp",
        "OpticsTemp",
        "LEXIbaseTemp",
        "HVsupplyTemp",
        "+5.2V_Imon",
        "+10V_Imon",
        "+3.3V_Imon",
        "AnodeVoltMon",
        "+28V_Imon",
        "ADC_Ground",
        "Cmd_count",
        "Pinpuller_Armed",
        "Unused1",
        "Unused2",
        "HVmcpAuto",
        "HVmcpMan",
        "DeltaEvntCount",
        "DeltaDroppedCount",
        "DeltaLostEvntCount",
    ]

    Date_datetime = [datetime.datetime.utcfromtimestamp(x) for x in all_data_dict["Date"]]

    df = pd.DataFrame(columns=df_key_list)
    for ii, key in enumerate(df_key_list):
        df[key] = all_data_dict[list(all_data_dict.keys())[ii]]

    # For the dataframe, replace the nans with the value from the previous index.
    # This is to make sure that the file isn't inundated with nans.
    for key in df.keys():
        for ii in range(1, len(df[key])):
            if np.isnan(df[key][ii]):
                # df[key][ii] = df[key][ii - 1]
                df.loc[ii, key] = df.loc[ii - 1, key]

    # Set the date column to the Date_datetime
    df["Date"] = Date_datetime

    # Set Date as the index without replacing the column
    df.set_index("Date", inplace=True, drop=False)
    # Split the file name in a folder and a file name
    # Format filenames and folder names for the different operating systems
    output_file_name = (
        os.path.basename(os.path.normpath(in_file_name)).split(".")[0] + "_hk_output_L1a.csv"
    )
    output_folder_name_list = os.path.dirname(os.path.normpath(in_file_name)).split("/")
    output_folder_name = (
        "/".join(output_folder_name_list[:-2]) + "/L1a/hk/" + output_folder_name_list[-1]
    )
    save_file_name = output_folder_name + "/" + output_file_name

    # Check if the save folder exists, if not then create it
    if not Path(output_folder_name).exists():
        Path(output_folder_name).mkdir(parents=True, exist_ok=True)

    # Save the dataframe to a csv file
    df.to_csv(save_file_name, index=False)

    return df, save_file_name


def read_binary_file(
    file_val=None,
):
    """
    Reads binary files from the level 0 data folder and returns the data frames for science and
    housekeeping packets.

    Parameters
    ----------
    file_val : str
        Name of the file to read.

    Returns
    -------
    file_name : str
        Name of the file.
    df_sci : pandas.DataFrame
        DataFrame of the science packet.
    df_hk : pandas.DataFrame
        DataFrame of the housekeeping packet.
    sci_save_filename : str
        Name of the file where the science packet is saved.
    hk_save_filename : str
        Name of the file where the housekeeping packet is saved.
    """
    file_name = file_val

    # Read the binary file and get the data frames
    df_sci, sci_save_filename = read_binary_data_sci(file_val)
    df_hk, hk_save_filename = read_binary_data_hk(file_val)

    return file_name, df_sci, df_hk, sci_save_filename, hk_save_filename
