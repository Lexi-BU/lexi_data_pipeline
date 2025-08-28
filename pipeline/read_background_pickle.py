import pickle

from astropy.io import fits
from astropy.wcs import WCS

with open("../data/background_files/pickle_files/2025-03-16T19:00:00.fits.pkl", "rb") as f:
    obj = pickle.load(f)

ra_edges = obj["ra_edges"]
dec_edges = obj["dec_edges"]
background = obj["background"]

# Rebuild a FITS Header from the dict, then construct WCS
h = fits.Header()
for k, (v, c) in obj["wcs_header_dict"].items():
    h[k] = (v, c)
w = WCS(h)  # ready to use
print(w)
