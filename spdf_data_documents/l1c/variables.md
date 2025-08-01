! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "Epoch"         CDF_EPOCH      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: 01-Jan-0000 00:00:00.000

  ! Attribute       Data
  ! Name            Type       Value
  ! --------        ----       -----

    "FIELDNAM"    CDF_CHAR     { "Time" }
    "VALIDMIN"    CDF_EPOCH    { 02-Mar-2025 08:00:00.000 }
    "VALIDMAX"    CDF_EPOCH    { 16-Mar-2025 21:45:59.000 }
    "SCALEMIN"    CDF_EPOCH    { 02-Mar-2025 00:00:00.000 }
    "SCALEMAX"    CDF_EPOCH    { 16-Mar-2025 23:59:59.000 }
    "LABLAXIS"    CDF_CHAR     { "Epoch" }
    "UNITS"       CDF_CHAR     { "ms" }
    "MONOTON"     CDF_CHAR     { "INCREASE" }
    "VAR_TYPE"    CDF_CHAR     { "support_data" }
    "FILLVAL"     CDF_EPOCH    { 31-Dec-9999 23:59:59.999 }
    "DICT_KEY"    CDF_CHAR     { "time>Epoch" }
    "CATDESC"     CDF_CHAR     { "Time, centered, in NSSDC Epoch" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { " " }
    "VAR_NOTES"   CDF_CHAR     { " " }
    "TIME_BASE"   CDF_CHAR     { "0 AD" } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "Epoch_unix"    CDF_UINT4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: 4294967294

  ! Attribute       Data
  ! Name            Type       Value
  ! --------        ----       -----

    "FIELDNAM"    CDF_CHAR     { "Time in Unix Epoch" }
    "VALIDMIN"    CDF_UINT4    { 1740902400 }
    "VALIDMAX"    CDF_UINT4    { 1742159748 }
    "SCALEMIN"    CDF_UINT4    { 1740873600 }
    "SCALEMAX"    CDF_UINT4    { 1742169599 }
    "LABLAXIS"    CDF_CHAR     { "Epoch Unix" }
    "UNITS"       CDF_CHAR     { "s" }
    "MONOTON"     CDF_CHAR     { "INCREASE" }
    "VAR_TYPE"    CDF_CHAR     { "support_data" }
    "FORMAT"      CDF_CHAR     { "I10" }
    "FILLVAL"     CDF_UINT4    { 4294967295 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "time>Epoch_unix" }
    "CATDESC"     CDF_CHAR     { "Time, centered, in Unix Epoch seconds" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { " " }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_x_mcp"
                  CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

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
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_x_mcp" }
    "CATDESC"     CDF_CHAR     { "Photon position in detector " -
                                 "coordinates, scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_y_mcp"
                  CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

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
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_y_mcp" }
    "CATDESC"     CDF_CHAR     { "Photon position in detector " -
                                 "coordinates, scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_RA"     CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

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
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_RA" }
    "CATDESC"     CDF_CHAR     { "Photon position in J2000 coordinates, " -
                                 "scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_Dec"    CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

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
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_Dec" }
    "CATDESC"     CDF_CHAR     { "Photon position in J2000 coordinates, " -
                                 "scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_az"     CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

  ! Attribute       Data
  ! Name            Type       Value
  ! --------        ----       -----

    "FIELDNAM"    CDF_CHAR     { "Photon azimuth angle in the local " -
                                 "topocentric coordinates" }
    "VALIDMIN"    CDF_REAL4    { 0.0 }
    "VALIDMAX"    CDF_REAL4    { 360.0 }
    "SCALEMIN"    CDF_REAL4    { 0.0 }
    "SCALEMAX"    CDF_REAL4    { 360.0 }
    "LABLAXIS"    CDF_CHAR     { "Azimuth" }
    "UNITS"       CDF_CHAR     { "deg" }
    "VAR_TYPE"    CDF_CHAR     { "data" }
    "FORMAT"      CDF_CHAR     { "f7.1" }
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_az" }
    "CATDESC"     CDF_CHAR     { "Photon azimuth angle in the local " -
                                 "topocentric coordinates, scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


! Variable          Data      Number                 Record   Dimension
! Name              Type     Elements  Dims  Sizes  Variance  Variances
! --------          ----     --------  ----  -----  --------  ---------

  "photon_el"     CDF_REAL4      1       0              T

  ! VAR_COMPRESSION: None
  ! (Valid compression: None, GZIP.1-9, RLE.0, HUFF.0, AHUFF.0)
  ! VAR_SPARSERECORDS: None
  ! (Valid sparserecords: None, sRecords.PAD, sRecords.PREV)
  ! VAR_PADVALUE: -1.0e+30

  ! Attribute       Data
  ! Name            Type       Value
  ! --------        ----       -----

    "FIELDNAM"    CDF_CHAR     { "Photon elevation angle in the local " -
                                 "topocentric coordinates" }
    "VALIDMIN"    CDF_REAL4    { -90.0 }
    "VALIDMAX"    CDF_REAL4    { 90.0 }
    "SCALEMIN"    CDF_REAL4    { -90.0 }
    "SCALEMAX"    CDF_REAL4    { 90.0 }
    "LABLAXIS"    CDF_CHAR     { "Elevation" }
    "UNITS"       CDF_CHAR     { "deg" }
    "VAR_TYPE"    CDF_CHAR     { "data" }
    "FORMAT"      CDF_CHAR     { "f7.1" }
    "FILLVAL"     CDF_REAL4    { -1.0e+31 }
    "DEPEND_0"    CDF_CHAR     { "Epoch" }
    "DICT_KEY"    CDF_CHAR     { "position>photon_el" }
    "CATDESC"     CDF_CHAR     { "Photon elevation angle in the local " -
                                 "topocentric coordinates, scalar" }
    "AVG_TYPE"    CDF_CHAR     { " " }
    "DISPLAY_TYPE"
                  CDF_CHAR     { "time_series" }
    "VAR_NOTES"   CDF_CHAR     { " " } .

  ! RV values were not requested.


#end
