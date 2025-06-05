    ! Variable        Data         Number                 Record   Dimension
    ! Name            Type         Elements  Dims  Sizes  Variance  Variances
    ! --------        ----         --------  ----  -----  --------  ---------  
    !"SW_P_Den"       CDF_REAL4       1        0              T


    ! Attribute       Data
    ! Name            Type         Value
    ! --------        ----         -----
      "CATDESC"       CDF_CHAR     { "Ion number density (Solar Wind " -
                                     "Analyzer), scalar" }
      "DEPEND_0"      CDF_CHAR     { "Epoch" }
      "DICT_KEY"      CDF_CHAR     { "density>ion_number" }
      "DISPLAY_TYPE"
                      CDF_CHAR     { "time_series" }
      "FIELDNAM"      CDF_CHAR     { "Ion Number Density (CPI/SWA)" }
      "FILLVAL"       CDF_REAL4    { -1.0e+31 }
      "FORMAT"        CDF_CHAR     { "f8.3" }
      "LABLAXIS"      CDF_CHAR     { "Ion N" }
      "UNITS"         CDF_CHAR     { "cm^3" }
      "VALIDMIN"      CDF_REAL4    { 0.01 }
      "VALIDMAX"      CDF_REAL4    { 1000.0 }
      "VAR_NOTES"     CDF_CHAR     { "Assuming no helium (0.3 - several " -
                                    "hundred) if the density is less than " -
                                    "0.3/cc the higher moments (VEL,TEMP) " -
                                    "shall not be used because of the poor " -
                                    "counting statistics." }
      "VAR_TYPE"      CDF_CHAR       { "data" }.