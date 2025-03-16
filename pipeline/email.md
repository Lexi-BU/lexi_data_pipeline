Dear LEXIers,
Apologies for taking this long to get the data to you all. The biggest issue I have faced so far is
that the calibration done on the ground for linear correction as well as non-linear correction
doesn't hold as is for the data we received from the spacecraft. Consequently, I had to simply the
first data product that I was hoping to provide the team. Below, I will briefly describe the data and
how I have processed it.

1. The level_0 is the raw data as received from LEXI and needs special code to read it. Ignore that
   for the most part.
2. L1a: This is the data that has been converted from the binary into csv format. Each file have the
   exact same data as the original binary file. The data though has been moved around top ensure that
   the files are placed in the folder with the data on which they were generated. There are both
   Housekeeping and Science data in these files. The Housekeeping data has the following columns:
   - Date
   - TimeStamp
   - HK_id
   - PinPullerTemp
   - OpticsTemp
   - LEXIbaseTemp
   - HVsupplyTemp
   - +5.2V_Imon
   - +10V_Imon
   - +3.3V_Imon
   - AnodeVoltMon
   - +28V_Imon
   - ADC_Ground
   - Cmd_count
   - Pinpuller_Armed
   - Unused1
   - Unused2
   - HVmcpAuto
   - HVmcpMan
   - DeltaEvntCount
   - DeltaDroppedCount
   - DeltaLostEvntCount
   Please refer to the LEXI ICD for more details on these parameters.
   The Science data has the following columns:
   - Date
   - TimeStamp
   - IsCommanded
   - Channel1
   - Channel2
   - Channel3
   - Channel4
   Please refer to the LEXI ICD for more details on these parameters.

   There are 48 folders in total, one for each day that LEXI has been in space and we have received
   the data for that day. Each folder has multiple files depending on the number of files received on
   that day.
3. L1b:
   a) Housekeeping: The housekeeping does not need to go through further processing. So, in the L1b
   version, I simply made the time length of each file uniform. Each file now is 1 hour long,
   described in their name. NOTE: that though all files, in their name, have 1 hour duration, the
   data in each file may not be exactly 1 hour long.

   b) Science: The science data has been processed and a few more columns are added:
   - channelx_shifted: This is the shift in the channelx voltage by either a fixed threshold value of
   2 or by the minimum value of that channel. This is only done for the science data points and the
   software data points are not shifted.
   - x_volt, y_volt: These are the x and y position of each photon in the dimensionless coordinate
   computed using the following equations:
   x_volt = channel3_shifted/(channel3_shifted + channel1_shifted)
   y_volt = channel2_shifted/(channel2_shifted + channel4_shifted)
   This equation helps normalize the data so that all the x_volt and y_volt values are between 0 and
   1.
   - x_cm, y_cm: These are the x and y position of each photon in cm computed using the following
   equations:
   x_cm = (x_volt - 0.5) * detector_diameter
   y_cm = (y_volt - 0.5) * detector_diameter
   where detector_diameter is the diameter of the LEXI effective area (for this case we have taken it
   to be 6 cm)

   Currently I am working on redoing the linear and non-linear correction algorithm based on data from the spacecraft. I will
   update you all once I have that ready. In the meantime, please feel free to reach out to me if you
   have any questions.

   NOTE: I have attached a simple python script that can be used to read the cdf files and generate a
   quick plot of the data. You will need to install the following packages:
   - numpy
   - matplotlib
   - spacepy
   - pandas
   Since the code was just something I randomly wrote, it is not well documented. Please feel free to
   reach out if you have any questions.

