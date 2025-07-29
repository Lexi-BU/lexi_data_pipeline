    ! Skeleton table for the "clps_bgm1_lexi_20250316_210000_to_20250316_220000_L1c_v0.0" CDF.
    ! Generated: Thursday, 24-Jul-2025 15:00:00
    ! CDF created/modified by CDF V2.5.18

    #header

                        CDF NAME: clps_bgm1_lexi_20250316_210000_to_20250316_220000_L1c_v0.0
                   DATA ENCODING: NETWORK
                        MAJORITY: COLUMN
                          FORMAT: SINGLE

    ! Variables  G.Attributes  V.Attributes  Records  Dims  Sizes
    ! ---------  ------------  ------------  -------  ----  -----
        8/0          17            18          1/z      1     3


    #GLOBALattributes

    ! Attribute         Entry       Data
    ! Name              Number      Type       Value
    ! ---------         ------      ----       -----

    "TITLE"               1:    CDF_CHAR     { "LEXI> Lunar Environment " -
                                                "Heliospheric X-ray Imager" } .

    "Project"             1:    CDF_CHAR     { "CLPS>Commercial Lunar Payload Services" } .

    "Discipline"          1:    CDF_CHAR     { "Space Physics>Magnetospheric Science" } .

    "Source_name"         1:    CDF_CHAR     { "BGM1>Blue Ghost Mission 1" } .

    "Descriptor"          1:    CDF_CHAR     { "LEXI>Lunar Environment " -
                                                "Heliospheric X-ray Imager" } .

    "Data_type"           1:    CDF_CHAR     { "Mn>Modified Data n" } .

    "Data_version"        1:    CDF_CHAR     { "1.0" } .

    "TEXT"                1:    CDF_CHAR     { "The lunar environment " -
                                               "heliophysics X-ray imager (LEXI) mission." }
                            2:    CDF_CHAR     { "BM Walsh, et al., Space " -
                                                 "Sci. Rev., accepted, 2024" } .

    "MODS"                1:    CDF_CHAR     { "TBD" } .

    "Logical_file_id"     1:    CDF_CHAR     { "clps_bgm1_lexi_20250316_210000" -
                                               "_to_20250316_220000_L1c_v0.0" } .

    "Logical_source"      1:    CDF_CHAR     { "LEXI" } .

    "Logical_source_description"
                            1:    CDF_CHAR     { "Lunar Environment Heliospheric " -
                                                 "X-ray Imager (LEXI)" } .

    "PI_name"             1:    CDF_CHAR     { "B. Walsh" } .

    "PI_affiliation"      1:    CDF_CHAR     { "Boston U." } .

    "Mission_group"       1:    CDF_CHAR     { "CLPS>Commercial Lunar Payload Services" } .

    "Instrument_type"     1:    CDF_CHAR     { "Imagers (space)" } .

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
    "FILLVAL"
    "DEPEND_0"
    "DEPEND_1"
    "DICT_KEY"
    "CATDESC"
    "AVG_TYPE"
    "DISPLAY_TYPE"
    "VAR_NOTES"


    #variables

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "Epoch"         CDF_EPOCH      1         T       F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Time" }
        "VALIDMIN"    CDF_EPOCH    { 16-Mar-2025 19:00:00.000 }
        "VALIDMAX"    CDF_EPOCH    { 16-Mar-2025 21:45:59.000 }
        "SCALEMIN"    CDF_EPOCH    { 16-Mar-2025 00:00:00.000 }
        "SCALEMAX"    CDF_EPOCH    { 16-Mar-2025 23:59:59.000 }
        "LABLAXIS"    CDF_CHAR     { "Epoch" }
        "UNITS"       CDF_CHAR     { "ms" }
        "MONOTON"     CDF_CHAR     { "INCREASE" }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FILLVAL"     CDF_REAL8    { -1.000000e+31 }
        "DICT_KEY"    CDF_CHAR     { "time>Epoch" }
        "CATDESC"     CDF_CHAR     { "Time, centered, in NSSDC Epoch" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.
    ! Variable        Data         Number                 Record   Dimension
    ! Name            Type         Elements  Dims  Sizes  Variance  Variances
    ! --------        ----         --------  ----  -----  --------  ---------  

    "Epoch_unix"     CDF_EPOCH      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Time in Unix Epoch" }
        "VALIDMIN"    CDF_EPOCH    { 1742151675 }
        "VALIDMAX"    CDF_EPOCH    { 1742159748 }
        "SCALEMIN"    CDF_EPOCH    { 1742151675 }
        "SCALEMAX"    CDF_EPOCH    { 1742159748 }
        "LABLAXIS"    CDF_CHAR     { "Epoch Unix" }
        "UNITS"       CDF_CHAR     { "s" }
        "MONOTON"     CDF_CHAR     { "INCREASE" }
        "VAR_TYPE"    CDF_CHAR     { "support_data" }
        "FILLVAL"     CDF_REAL8    { -1.000000e+31 }
        "DICT_KEY"    CDF_CHAR     { "time>Epoch_unix" }
        "CATDESC"     CDF_CHAR     { "Time, centered, in Unix Epoch seconds" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { "RV values were not requested." } .

    ! RV values were not requested.

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_x_mcp"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Photon position in detector coordinates" }
        "VALIDMIN"    CDF_REAL4    { -5.0 }
        "VALIDMAX"    CDF_REAL4    { 5.0 }
        "SCALEMIN"    CDF_REAL4    { -5.0 }
        "SCALEMAX"    CDF_REAL4    { 5.0 }
        "LABLAXIS"    CDF_CHAR     { "X MCP" }
        "UNITS"       CDF_CHAR     { "cm" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_x_mcp" }
        "CATDESC"     CDF_CHAR     { "Photon position in detector coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_y_mcp"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon position in detector coordinates" }
        "VALIDMIN"    CDF_REAL4    { -5.0 }
        "VALIDMAX"    CDF_REAL4    { 5.0 }
        "SCALEMIN"    CDF_REAL4    { -5.0 }
        "SCALEMAX"    CDF_REAL4    { 5.0 }
        "LABLAXIS"    CDF_CHAR     { "Y MCP" }
        "UNITS"       CDF_CHAR     { "cm" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_y_mcp" }
        "CATDESC"     CDF_CHAR     { "Photon position in detector coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_RA"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon position in J2000 coordinates" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 360.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 360.0 }
        "LABLAXIS"    CDF_CHAR     { "RA" }
        "UNITS"       CDF_CHAR     { "deg" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_RA" }
        "CATDESC"     CDF_CHAR     { "Photon position in J2000 coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_dec"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon position in J2000 coordinates" }
        "VALIDMIN"    CDF_REAL4    { -90.0 }
        "VALIDMAX"    CDF_REAL4    { 90.0 }
        "SCALEMIN"    CDF_REAL4    { -90.0 }
        "SCALEMAX"    CDF_REAL4    { 90.0 }
        "LABLAXIS"    CDF_CHAR     { "DEC" }
        "UNITS"       CDF_CHAR     { "deg" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_dec" }
        "CATDESC"     CDF_CHAR     { "Photon position in J2000 coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_az"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon azimuth angle in the local topocentric coordinates" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 360.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 360.0 }
        "LABLAXIS"    CDF_CHAR     { "Azimuth" }
        "UNITS"       CDF_CHAR     { "deg" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_az" }
        "CATDESC"     CDF_CHAR     { "Photon azimuth angle in the local topocentric coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.

    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "photon_el"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon elevation angle in the local topocentric coordinates" }
        "VALIDMIN"    CDF_REAL4    { -90.0 }
        "VALIDMAX"    CDF_REAL4    { 90.0 }
        "SCALEMIN"    CDF_REAL4    { -90.0 }
        "SCALEMAX"    CDF_REAL4    { 90.0 }
        "LABLAXIS"    CDF_CHAR     { "Elevation" }
        "UNITS"       CDF_CHAR     { "deg" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>photon_el" }
        "CATDESC"     CDF_CHAR     { "Photon elevation angle in the local topocentric coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " "}
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.

    #zvariables

    ! No zvariables.

    #end