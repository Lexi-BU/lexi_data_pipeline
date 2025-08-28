import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

fits_file = "lexi_l2_az_el_5min_counts.fits"

# --- Open and read ---
with fits.open(fits_file) as hdul:
    data_cube = hdul[0].data  # shape = (time, y, x)
    hdr = hdul[0].header
    bins_tbl = hdul["BINS"].data  # bin edges table

# Extract edges from the table
time_edges = bins_tbl["TIME_EDGES_S"][0]
x_edges = bins_tbl["X_EDGES_DEG"][0]
y_edges = bins_tbl["Y_EDGES_DEG"][0]

# Choose which slice to plot (e.g., first time bin)
slice_idx = 0
hist2d = data_cube[slice_idx]

# Alternatively, sum over all time bins:
# hist2d = data_cube.sum(axis=0)

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 6))
# Note: imshow expects pixel centers; use extent to label in degrees
extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
im = ax.imshow(hist2d, origin="lower", extent=extent, aspect="auto", cmap="inferno")
cb = fig.colorbar(im, ax=ax)
cb.set_label(hdr.get("BUNIT", "Counts"))

ax.set_xlabel(hdr.get("CTYPE1", "X") + f" [{hdr.get('CUNIT1','deg')}]")
ax.set_ylabel(hdr.get("CTYPE2", "Y") + f" [{hdr.get('CUNIT2','deg')}]")
ax.set_title(f"Histogram for time bin {slice_idx} " f"({hdr.get('DATE-BEG','')})")

plt.tight_layout()
plt.savefig("histogram_slice.png", dpi=200)
plt.close(fig)

print("Saved histogram to histogram_slice.png")
