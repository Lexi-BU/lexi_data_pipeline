    ! Variable        Data         Number                 Record   Dimension
    ! Name            Type         Elements  Dims  Sizes  Variance  Variances
    ! --------        ----         --------  ----  -----  --------  ---------  

    "Epoch"         CDF_EPOCH      1         T         F

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
        "CATDESC"     CDF_CHAR     { "LEXI s/c position, 3 comp. in GSE coord." }
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
        "CATDESC"     CDF_CHAR     { "Label for LEXI Position (GSE)" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { " " }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! NRV values follow...

        [1] = { "LEXI X (GSE)" }
        [2] = { "LEXI Y (GSE)" }
        [3] = { "LEXI Z (GSE)" }


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
        "LABLAXIS"    CDF_CHAR     { "LEXI Rad Dist" }
        "UNITS"       CDF_CHAR     { "km" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f9.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>radial_distance" }
        "CATDESC"     CDF_CHAR     { "LEXI s/c radial distance to center of " -
                                    "Earth, scalar" }
        "AVG_TYPE"    CDF_CHAR     { "standard" }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "x_mcp"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Photon position in detector coordinates" }
        "VALIDMIN"    CDF_REAL4    { -1 }
        "VALIDMAX"    CDF_REAL4    { 1.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "X MCP" }
        "UNITS"       CDF_CHAR     { "#" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>x_mcp" }
        "CATDESC"     CDF_CHAR     { "Photon position in detector coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------

    "y_mcp"            CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----

        "FIELDNAM"    CDF_CHAR     { "Photon position in detector coordinates" }
        "VALIDMIN"    CDF_REAL4    { -1 }
        "VALIDMAX"    CDF_REAL4    { 1.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "Y MCP" }
        "UNITS"       CDF_CHAR     { "#" }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>y_mcp" }
        "CATDESC"     CDF_CHAR     { "Photon position in detector coordinates, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------
    "lexi_ra"          CDF_REAL4      1         T         F

    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon RA in J2000 coordinates" }
        "VALIDMIN"    CDF_REAL4    { 0.0 }
        "VALIDMAX"    CDF_REAL4    { 180.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "RA J2000" }
        "UNITS"       CDF_CHAR     { "#Deg." }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>lexi_ra" }
        "CATDESC"     CDF_CHAR     { "Photon RA in J2000, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .

    ! RV values were not requested.


    ! Variable          Data      Number    Record   Dimension
    ! Name              Type     Elements  Variance  Variances
    ! --------          ----     --------  --------  ---------
    "lexi_dec"         CDF_REAL4      1         T         F
    
    ! Attribute       Data
    ! Name            Type       Value
    ! --------        ----       -----
        "FIELDNAM"    CDF_CHAR     { "Photon DEC in J2000 coordinates" }
        "VALIDMIN"    CDF_REAL4    { -90.0 }
        "VALIDMAX"    CDF_REAL4    { 90.0 }
        "SCALEMIN"    CDF_REAL4    { 0.0 }
        "SCALEMAX"    CDF_REAL4    { 200.0 }
        "LABLAXIS"    CDF_CHAR     { "DEC J2000" }
        "UNITS"       CDF_CHAR     { "#Deg." }
        "VAR_TYPE"    CDF_CHAR     { "data" }
        "FORMAT"      CDF_CHAR     { "f7.1" }
        "FILLVAL"     CDF_REAL4    { -1.000000e+31 }
        "DEPEND_0"    CDF_CHAR     { "Epoch" }
        "DICT_KEY"    CDF_CHAR     { "position>lexi_dec" }
        "CATDESC"     CDF_CHAR     { "Photon DEC in J2000, scalar" }
        "AVG_TYPE"    CDF_CHAR     { " " }
        "DISPLAY_TYPE"
                    CDF_CHAR     { "time_series" }
        "VAR_NOTES"   CDF_CHAR     { " " } .
    
