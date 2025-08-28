import re

import numpy as np
from astropy.io import fits
from astropy.table import Table

path = "../data/background_files/lexi_path.fits"


def find_best(colnames, patterns):
    """
    Return the first column name that matches any of the regex patterns (case-insensitive).
    """
    names_lower = [c.lower() for c in colnames]
    for pat in patterns:
        rx = re.compile(pat, re.IGNORECASE)
        for orig, low in zip(colnames, names_lower):
            if rx.fullmatch(low) or rx.search(low):
                return orig
    return None


with fits.open(path) as hdul:
    hdul.info()
    # Case A: look for a BinTable extension with expected columns
    table_hdu_idx = None
    for i, hdu in enumerate(hdul[1:], start=1):
        if isinstance(hdu, fits.BinTableHDU):
            table_hdu_idx = i
            break

    if table_hdu_idx is not None:
        print(f"\nFound table in extension {table_hdu_idx}. Columns:")
        print(hdul[table_hdu_idx].columns)

        tab = Table.read(path, hdu=table_hdu_idx)
        cols = tab.colnames

        # Try to locate likely column names (be forgiving about naming)
        # Time
        time_col = find_best(cols, [r"^time$", r"^t$", r".*mjd.*", r".*utc.*", r".*epoch.*"])
        # RA/Dec for pointing (per time step)
        ra_col = find_best(cols, [r"^ra$", r".*ra(_?deg)?$", r".*ra.*"])
        dec_col = find_best(cols, [r"^de$", r"^del?$", r".*de(_?deg)?$", r".*de.*"])
        # d_2 axis RA/Dec
        d2_ra = find_best(cols, [r"^(d2_)?ra(_?deg)?$", r".*d.?2.*ra.*"])
        d2_dec = find_best(cols, [r"^(d2_)?de(_?deg)?$", r".*d.?2.*de.*"])
        # Position angle
        pa_y = find_best(cols, [r"^pa[_-]?y$", r"^pay$", r".*pos.*angle.*y.*", r".*\bpa\b.*"])

        # Show what we found
        print("\nMatched columns:")
        print(" time:", time_col)
        print("   RA:", ra_col)
        print("  Dec:", dec_col)
        print(" d2RA:", d2_ra)
        print("d2Dec:", d2_dec)
        print(" PA_Y:", pa_y)

        # Extract arrays (only if present)
        def get_or_none(name):
            return np.array(tab[name]) if name in tab.colnames else None

        time = get_or_none(time_col) if time_col else None
        ra = get_or_none(ra_col) if ra_col else None
        dec = get_or_none(dec_col) if dec_col else None
        d2ra = get_or_none(d2_ra) if d2_ra else None
        d2de = get_or_none(d2_dec) if d2_dec else None
        pay = get_or_none(pa_y) if pa_y else None

        # Minimal sanity printout
        print("\nShapes:")
        for n, arr in [
            ("time", time),
            ("ra", ra),
            ("dec", dec),
            ("d2_ra", d2ra),
            ("d2_dec", d2de),
            ("pa_y", pay),
        ]:
            if arr is not None:
                print(f" {n}: {arr.shape}, example: {arr[0] if len(arr) else 'empty'}")

        # At this point you have numpy arrays. Example: first few rows
        if ra is not None and dec is not None:
            print("\nFirst 3 (RA, Dec):")
            for k in range(min(3, len(ra))):
                print(f"  {k}: {ra[k]}, {dec[k]}")

    else:
        # Case B: maybe it’s an image/cube with WCS in some HDU (but your info() showed none)
        if hdul[0].data is not None and hdul[0].data.size > 0:
            print("\nPrimary contains image data. You can build WCS like:")
            from astropy.wcs import WCS

            w = WCS(hdul[0].header)
            print(w)
        else:
            # Case C: truly header-only
            print("\nThis FITS has no data arrays and no table extensions.")
            print("If you expected RA/Dec/PA_Y per time step, you likely need a different file")
            print("(the one that actually contains a BinTableHDU with those columns).")
