import glob
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

fits_folder = "../data/background_files/fits_files/1min/"
fits_files = sorted(glob.glob(fits_folder + "*.fits.gz"))

for fits_file in fits_files[:1]:
    with fits.open(fits_file) as hdul:
        hdu = hdul[0]
        data = np.asarray(hdu.data, dtype=float)
        hdr = hdu.header

    ny, nx = data.shape
    w = WCS(hdr)

    # --- Create pixel grid (edges, not centers) ---
    # Pixel coordinates in FITS are 1-based, so +0.5 shifts to pixel edges
    y_edges, x_edges = np.mgrid[0 : ny + 1, 0 : nx + 1]

    # Convert pixel edges to world coords (RA/Dec)
    # 'origin=0' → use 0-based pixel convention
    ra_edges, dec_edges = w.all_pix2world(x_edges, y_edges, 0)

    # --- Plot with RA/Dec axes ---
    fig, ax = plt.subplots(figsize=(6, 5))

    mesh = ax.pcolormesh(ra_edges, dec_edges, data, cmap="jet", shading="auto")

    plt.colorbar(mesh, ax=ax, label="Intensity")
    ax.set_xlabel("Right Ascension [deg]")
    ax.set_ylabel("Declination [deg]")
    ax.set_title(hdr.get("OBJECT", "FITS Image"))

    # Optional: invert RA axis (astronomical convention: RA increases to the left)
    ax.invert_xaxis()

    plt.tight_layout()
    plt.show()
