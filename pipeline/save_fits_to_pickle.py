import glob
import pickle
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

fits_folder = "../data/background_files/fits_files/1min/"
fits_files = sorted(glob.glob(fits_folder + "*.fits.gz"))

out_dir = Path("../data/background_files/pickle_files/")
out_dir.mkdir(parents=True, exist_ok=True)

for fits_file in fits_files[:1]:
    with fits.open(fits_file) as hdul:
        hdu = hdul[0]
        data = np.asarray(hdu.data, dtype=float)
        hdr = hdu.header

    ny, nx = data.shape
    w = WCS(hdr)

    # Pixel-edge grids (for pcolormesh)
    y_edges, x_edges = np.mgrid[0 : ny + 1, 0 : nx + 1]
    ra_edges, dec_edges = w.all_pix2world(x_edges, y_edges, 0)

    # Serialize WCS header safely as dict of (value, comment) pairs
    wcs_h = w.to_header(relax=True)
    wcs_header_dict = {k: (wcs_h[k], wcs_h.comments[k]) for k in wcs_h.keys()}

    payload = {
        "ra_edges": ra_edges.astype(np.float64),
        "dec_edges": dec_edges.astype(np.float64),
        "background": data.astype(np.float32),
        "wcs_header_dict": wcs_header_dict,
    }

    out_pkl = out_dir / (Path(fits_file).stem + ".pkl")
    with open(out_pkl, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Saved: {out_pkl.resolve()}")
