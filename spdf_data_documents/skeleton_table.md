    ! Skeleton table for the "wi_k0_swe_00000000_v01" CDF.
    ! Generated: Monday, 4-Mar-1996 12:03:10
    ! CDF created/modified by CDF V2.5.18
    ! Skeleton table created by CDF V2.5.18 

    #header

                        CDF NAME: wi_k0_swe_00000000_v01
                    DATA ENCODING: NETWORK
                        MAJORITY: COLUMN
                            FORMAT: SINGLE

    ! Variables  G.Attributes  V.Attributes  Records  Dims  Sizes
    ! ---------  ------------  ------------  -------  ----  -----
        30/0          18            23         1/z      1     3


    #GLOBALattributes

    ! Attribute         Entry       Data
    ! Name              Number      Type       Value
    ! ---------         ------      ----       -----

    "TITLE"               1:    CDF_CHAR     { "WIND> Solar Wind Parameters" } .

    "Project"             1:    CDF_CHAR     { " ISTP>International " -
                                                "Solar-Terrestrial Physics" } .

    "Discipline"          1:    CDF_CHAR     { "Space " -
                                                "Physics>Interplanetary " -
                                                "Studies" } .

    "Source_name"         1:    CDF_CHAR     { "WIND>Wind Interplanetary " -
                                                "Plasma Laboratory" } .

    "Descriptor"          1:    CDF_CHAR     { "SWE>Solar Wind Experiment" } .

    "Data_type"           1:    CDF_CHAR     { "K0>Key Parameter" } .

    "Data_version"        1:    CDF_CHAR     { "1" } .

    "TEXT"                1:    CDF_CHAR     { "SWE, a comprehensive " -
                                                "plasma instrument for the " -
                                                "WIND spacecraft, K.W." }
                            2:    CDF_CHAR     { "Ogilvie, et al., Space " -
                                                "Sci. Rev., accepted, 1994" } .

    "MODS"                1:    CDF_CHAR     { "TBD" } .

    "ADID_ref"            1:    CDF_CHAR     { "NSSD0138" } .

    "Logical_file_id"     1:    CDF_CHAR     { "WI_K0_SWE_00000000_V01" } .

    "Logical_source"      1:    CDF_CHAR     { "WI_K0_SWE" } .

    "Logical_source_description"
                            1:    CDF_CHAR     { "Wind Solar Wind " -
                                                "Experiment, Key Parameters" } .

    "PI_name"             1:    CDF_CHAR     { "K. Ogilvie" } .

    "PI_affiliation"      1:    CDF_CHAR     { "NASA GSFC" } .

    "Mission_group"       1:    CDF_CHAR     { "Wind" } .

    "Instrument_type"     1:    CDF_CHAR     { "Plasma and Solar Wind" } .

    "TEXT_supplement_1"
                            1:    CDF_CHAR     { " " } .


    #VARIABLEattributes

    "FIELDNAM"
    "VALIDMIN"
    "VALIDMAX"
    "SCALEMIN"
    "SCALEMAX"
    "LABLAXIS"
    "UNITS"
    "MONOTON"
    "VAR_TYPE"
    "FORMAT"
    "FORM_PTR"
    "LABL_PTR_1"
    "UNIT_PTR"
    "FILLVAL"
    "DEPEND_0"
    "DEPEND_1"
    "DICT_KEY"
    "CATDESC"
    "DELTA_PLUS_VAR"
    "DELTA_MINUS_VAR"
    "AVG_TYPE"
    "DISPLAY_TYPE"
    "VAR_NOTES"


    #variables

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Epoch"         CDF_EPOCH      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Time" }
        "VALIDMIN"    CDF_EPOCH    { 01-Nov-1994 00:00:00.000 }
        "VALIDMAX"    CDF_EPOCH    { 31-Dec-2020 23:59:59.000 }
        "SCALEMIN"    CDF_EPOCH    { 01-Nov-1994 00:00:00.000 }
        "SCALEMAX"    CDF_EPOCH    { 31-Dec-2020 23:59:59.000 }
        "LABLAXIS"    CDF_CHAR     { "Epoch" }
        "UNITS"       CDF_CHAR     { "ms" }
        "MONOTON"     CDF_CHAR     { "INCREASE" }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FILLVAL"     CDF_REAL8    { -1.000000e+31 }
        "DICT_KEY"    CDF_CHAR     { "time>Epoch" }
        "CATDESC"     CDF_CHAR     { "Time, centered, in NSSDC Epoch" }
        "DELTA_PLUS_VAR"
                    CDF_CHAR     { "Delta_time" }
        "DELTA_MINUS_VAR"
                    CDF_CHAR     { "Delta_time" }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Delta_time"    CDF_REAL8      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Time interval" }
        "VALIDMIN"    CDF_REAL8    { 0.0 }
        "VALIDMAX"    CDF_REAL8    { 300000.0 }
        "SCALEMIN"    CDF_REAL8    { 2000.0 }
        "SCALEMAX"    CDF_REAL8    { 200000.0 }
        "LABLAXIS"    CDF_CHAR     { "Del Time" }
        "UNITS"       CDF_CHAR     { "ms" }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "E10.4" }
        "FILLVAL"     CDF_REAL8    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "time" }
        "CATDESC"     CDF_CHAR     { "1/2 time interval to collect data for " -
                                    "parameters " }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Time_PB5"      CDF_INT4       1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Time PB5" }
        "VALIDMIN"    CDF_INT4     { 1994, 305, 0 }
        "VALIDMAX"    CDF_INT4     { 2020, 365, 86399000 }
        "SCALEMIN"    CDF_INT4     { 1994, 305, 0 }
        "SCALEMAX"    CDF_INT4     { 2020, 365, 86399000 }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORM_PTR"    CDF_CHAR     { "format_time" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_time" }
        "UNIT_PTR"    CDF_CHAR     { "unit_time" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "unit_time" }
        "DICT_KEY"    CDF_CHAR     { "time>PB5" }
        "CATDESC"     CDF_CHAR     { "Time, centered, in GSFC PB5 format " -
                                    "(yr, day, ms)" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "unit_time"     CDF_CHAR       4         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Units for Time_PB5" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Units for Time_PB5" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "year" }
        [2] = { "day " }
        [3] = { "msec" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_time"    CDF_CHAR      27         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Label for Time_PB5" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Label for Time_PB5" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "Year                       " }
        [2] = { "Day of Year (Jan 1 = Day 1)" }
        [3] = { "Elapsed millisecond of day " }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "format_time"   CDF_CHAR       2         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Format for Time_PB5" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Format for Time_PB5" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "I4" }
        [2] = { "I3" }
        [3] = { "I8" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "GAP_FLAG"      CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Post Gap Flag" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 15 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 3 }
        "LABLAXIS"    CDF_CHAR     { "Data Gap" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I2" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>post_gap" }
        "CATDESC"     CDF_CHAR     { "Post Gap Flag0=no gap immediately " -
                                    "prior to this record; other:see " -
                                    "'Guidelines' " }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "MODE"          CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Instrument Mode" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 15 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 5 }
        "LABLAXIS"    CDF_CHAR     { "Mode" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I2" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>mode" }
        "CATDESC"     CDF_CHAR     { "Mode categories to be decided" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "SC_pos_gse"    CDF_REAL4      1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "S/C position in GSE" }
        "VALIDMIN"    CDF_REAL4    { -2.000000e+06, -2.000000e+06,
                                    -2.000000e+06 }
        "VALIDMAX"    CDF_REAL4    { 2.000000e+06, 2.000000e+06, 2.000000e+06 }
        "SCALEMIN"    CDF_REAL4    { -2.000000e+06, -2.000000e+06,
                                    -2.000000e+06 }
        "SCALEMAX"    CDF_REAL4    { 2.000000e+06, 2.000000e+06, 2.000000e+06 }
        "UNITS"       CDF_CHAR     { "km" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f9.1" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_pos_GSE" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "cartesian" }
        "DICT_KEY"    CDF_CHAR     { "position>GSE_cartesian" }
        "CATDESC"     CDF_CHAR     { "Wind s/c position, 3 comp. in GSE coord." }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_pos_GSE"
                    CDF_CHAR      10         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Label for POS(GSE)" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Label for Wind Position (GSE)" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "WI X (GSE)" }
        [2] = { "WI Y (GSE)" }
        [3] = { "WI Z (GSE)" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "SC_pos_GSM"    CDF_REAL4      1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "S/C position in GSM" }
        "VALIDMIN"    CDF_REAL4    { -2.000000e+06, -2.000000e+06,
                                    -2.000000e+06 }
        "VALIDMAX"    CDF_REAL4    { 2.000000e+06, 2.000000e+06, 2.000000e+06 }
        "SCALEMIN"    CDF_REAL4    { -2.000000e+06, -2.000000e+06,
                                    -2.000000e+06 }
        "SCALEMAX"    CDF_REAL4    { 2.000000e+06, 2.000000e+06, 2.000000e+06 }
        "UNITS"       CDF_CHAR     { "km" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f9.1" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_pos_GSM" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "cartesian" }
        "DICT_KEY"    CDF_CHAR     { "position>GSM_cartesian" }
        "CATDESC"     CDF_CHAR     { "Wind s/c position, 3 comp. in GSM coord." }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_pos_GSM"
                    CDF_CHAR      10         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Label for POS(GSM)" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Label for Wind POS(GSM)" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "WI X (GSM)" }
        [2] = { "WI Y (GSM)" }
        [3] = { "WI Z (GSM)" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "SC_pos_R"      CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "S/C radial distance" }
        "VALIDMIN"    CDF_REAL4    { 6400.0 }
        "VALIDMAX"    CDF_REAL4    { 4.000000e+06 }
        "SCALEMIN"    CDF_REAL4    { 6400.0 }
        "SCALEMAX"    CDF_REAL4    { 4.000000e+06 }
        "LABLAXIS"    CDF_CHAR     { "WI Rad Dist" }
        "UNITS"       CDF_CHAR     { "km" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f9.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>radial_distance" }
        "CATDESC"     CDF_CHAR     { "Wind s/c radial distance to center of " -
                                    "Earth, scalar" }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "DQF"           CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Quality Flag: Data" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 1 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 1 }
        "LABLAXIS"    CDF_CHAR     { "DQ FLAG" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I1" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>quality" }
        "CATDESC"     CDF_CHAR     { "Data Quality Flag: 0=good; 1=bad" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "QF_V"          CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Quality Flag: Velocity" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 2147483647 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 256 }
        "LABLAXIS"    CDF_CHAR     { "QF_V" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I11" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>quality" }
        "CATDESC"     CDF_CHAR     { "Velocity Quality Flag: 0=OK; 2 or 130 " -
                                    "= caution; Other values NOT VALID" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { "Velocity Quality Flag: 0=OK; " -
                                    "2=parabolic 3-point fit only; " -
                                    "130=parabolic 3-point fit only, sensor" -
                                    " 1 only, N/S angle zero degrees " -
                                    "assumed; Other values NOT VALID" } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "QF_Vth"        CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Quality Flag: proton Vth" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 2147483647 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 255 }
        "LABLAXIS"    CDF_CHAR     { "QF_Vth" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I11" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>quality" }
        "CATDESC"     CDF_CHAR     { "Proton thermal speed Quality Flag: " -
                                    "0=OK; 2 or 130 = caution; Other values" -
                                    " NOT VALID" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { "Proton thermal speed Quality Flag: " -
                                    "0=OK; 2=parabolic 3-point fit only; " -
                                    "130=parabolic 3-point fit only, sensor" -
                                    " 1 only, N/S angle zero degrees " -
                                    "assumed; Other values NOT VALID" } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "QF_Np"         CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Quality Flag: proton dens." }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 2147483647 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 255 }
        "LABLAXIS"    CDF_CHAR     { "QF_Np" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I11" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>quality" }
        "CATDESC"     CDF_CHAR     { "Proton Density Quality Flag: 0=OK; 2 " -
                                    "or 130 = caution; Other values NOT " -
                                    "VALID" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { "Proton Density Quality Flag: 0=OK; " -
                                    "2=parabolic 3-point fit only; " -
                                    "130=parabolic 3-point fit only, sensor" -
                                    " 1 only, N/S angle zero degrees " -
                                    "assumed; Other values NOT VALID" } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "QF_a/p"        CDF_INT4       1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Quality Flag: Na/Np" }
        "VALIDMIN"    CDF_INT4     { 0 }
        "VALIDMAX"    CDF_INT4     { 2147483647 }
        "SCALEMIN"    CDF_INT4     { 0 }
        "SCALEMAX"    CDF_INT4     { 256 }
        "LABLAXIS"    CDF_CHAR     { "QF_a/p" }
        "UNITS"       CDF_CHAR     { " " }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FORMAT"      CDF_CHAR     { "I11" }
        "FILLVAL"     CDF_INT4     { -2147483648 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "flag>quality" }
        "CATDESC"     CDF_CHAR     { "Na/Np Quality Flag: 0=OK; >0=NOT VALID" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "V_GSE"         CDF_REAL4      1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Solar Wind Velocity (GSE)" }
        "VALIDMIN"    CDF_REAL4    { -1800.0, -900.0, -900.0 }
        "VALIDMAX"    CDF_REAL4    { 0.0, 900.0, 900.0 }
        "SCALEMIN"    CDF_REAL4    { -1200.0, -500.0, -500.0 }
        "SCALEMAX"    CDF_REAL4    { 0.0, 500.0, 500.0 }
        "UNITS"       CDF_CHAR     { "km/s" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f8.1" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_V_GSE" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "cartesian" }
        "DICT_KEY"    CDF_CHAR     { "velocity>solar_wind_GSE" }
        "CATDESC"     CDF_CHAR     { "Solar Wind Velocity in GSE coord., 3 " -
                                    "comp." }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_V_GSE"   CDF_CHAR       8         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "label VELOCITY (GSE)" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label>velocity" }
        "CATDESC"     CDF_CHAR     { "label, Solar wind velocity, GSE" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "VX (GSE)" }
        [2] = { "VY (GSE)" }
        [3] = { "VZ (GSE)" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "V_GSM"         CDF_REAL4      1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Solar Wind Velocity (GSM)" }
        "VALIDMIN"    CDF_REAL4    { -1800.0, -900.0, -900.0 }
        "VALIDMAX"    CDF_REAL4    { 0.0, 900.0, 900.0 }
        "SCALEMIN"    CDF_REAL4    { -1200.0, -500.0, -500.0 }
        "SCALEMAX"    CDF_REAL4    { 0.0, 500.0, 500.0 }
        "UNITS"       CDF_CHAR     { "km/s" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f8.1" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_V_GSM" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "cartesian" }
        "DICT_KEY"    CDF_CHAR     { "velocity>solar_wind_GSM" }
        "CATDESC"     CDF_CHAR     { "Solar Wind Velocity in GSM coord., 3 " -
                                    "comp." }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_V_GSM"   CDF_CHAR       8         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "label VELOCITY (GSM)" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label>velocity" }
        "CATDESC"     CDF_CHAR     { "label, Solar wind velocity, GSM" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "VX (GSM)" }
        [2] = { "VY (GSM)" }
        [3] = { "VZ (GSM)" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "V_GSE_p"       CDF_REAL4      1         T         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Bulk Flow, polar, (GSE) " }
        "VALIDMIN"    CDF_REAL4    { 0.0, -50.0, -50.0 }
        "VALIDMAX"    CDF_REAL4    { 2000.0, 50.0, 50.0 }
        "SCALEMIN"    CDF_REAL4    { 200.0, -20.0, -20.0 }
        "SCALEMAX"    CDF_REAL4    { 1000.0, 20.0, 20.0 }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f6.1" }
        "LABL_PTR_1"
                    CDF_CHAR     { "label_V_polar" }
        "UNIT_PTR"    CDF_CHAR     { "unit_polar" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DEPEND_1"    CDF_CHAR     { "polar" }
        "DICT_KEY"    CDF_CHAR     { "velocity>polar_GSE" }
        "CATDESC"     CDF_CHAR     { "Ion Bulk Flow vector in GSE coord.,  3" -
                                    " comp. (speed, E/W flow, N/S flow)" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "label_V_polar"
                    CDF_CHAR      13         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "FLOW ANGLES (GSE)" }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label>velocity" }
        "CATDESC"     CDF_CHAR     { "Flow direction: +E/W=from W of SUN; " -
                                    "+N/S=from S of SUN" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "Flow Speed   " }
        [2] = { "E/W Flow(GSE)" }
        [3] = { "N/S Flow(GSE)" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "unit_polar"    CDF_CHAR       4         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "units for V_polar " }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label>units" }
        "CATDESC"     CDF_CHAR     { "units for V_polar                       " }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "KM/S" }
        [2] = { "DEG " }
        [3] = { "DEG " }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "THERMAL_SPD"   CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Proton thermal speed" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 500.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "SW Vth" }
        "UNITS"       CDF_CHAR     { "km/s" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f6.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "velocity>thermal_speed" }
        "CATDESC"     CDF_CHAR     { "Solar Wind Most Probable Thermal Speed" -
                                    " = sqrt(2kT/M), scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Np"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Proton density" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 1000.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "Ion N" }
        "UNITS"       CDF_CHAR     { "#/cc" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "density" }
        "CATDESC"     CDF_CHAR     { "Solar Wind Proton Number Density, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Alpha Percent"
                    CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Alpha Percent" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 100.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 100.0 }
        "LABLAXIS"    CDF_CHAR     { "Na/Np" }
        "UNITS"       CDF_CHAR     { "%" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.3" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "ratio" }
        "CATDESC"     CDF_CHAR     { "Percent of density due to alpha " -
                                    "particles" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "cartesian"     CDF_CHAR       1         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Components in Cartesian Coord." }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "3 Components in Cartesian Coord." }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "x" }
        [2] = { "y" }
        [3] = { "z" }


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "polar"         CDF_CHAR       3         F         T

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Components in Polar Coord." }
        "VAR_TYPE"    CDF_CHAR     { "metadata" }
        "DICT_KEY"    CDF_CHAR     { "label" }
        "CATDESC"     CDF_CHAR     { "Flow(GSE): LON=arctan[VY/-VX]; " -
                                    "LAT=arctan[VZ/sqrt[VX**2+VY**2]" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "mag" }
        [2] = { "lon" }
        [3] = { "lat" }


    #zVariables

    ! No zVariables.


    #end