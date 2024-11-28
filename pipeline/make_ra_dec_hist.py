from spacepy.pycdf import CDF
import numpy as np
import matplotlib.pyplot as plt
import glob

folder_name = "/home/vetinari/Desktop/git/Lexi-Bu/lexi_data_pipeline/data/from_lexi/2024/processed_data/sci/level_1c/cdf/1.0.0"

file_name_list = np.sort(glob.glob(folder_name + "/*.cdf"))

ra_list = []
dec_list = []
epoch_unix_list = []

for file_name in file_name_list[:]:
    dat = CDF(file_name)
    ra_list.append(dat["ra_J2000_deg"][:])
    dec_list.append(dat["dec_J2000_deg"][:])
    epoch_unix_list.append(dat["Epoch"][:])
    dat.close()


# Turn on the latex rendering
plt.rc("text", usetex=True)
plt.rc("font", family="serif")

ra = np.concatenate(ra_list)
dec = np.concatenate(dec_list)
epoch_unix = np.concatenate(epoch_unix_list)

# Get the indices where ra is not in the range 0 to 360 and dec is not in the range -90 to 90
bad_indices = np.where(
    (ra < 0) | (ra > 360) | np.isnan(ra) | (dec < -90) | (dec > 90) | np.isnan(dec)
)

# Remove the bad indices
ra = np.delete(ra, bad_indices)
dec = np.delete(dec, bad_indices)

ra_min = np.nanmax([0, np.nanmin(ra)])
ra_max = np.nanmin([360, np.nanmax(ra)])
dec_min = np.nanmax([-90, np.nanmin(dec)])
dec_max = np.nanmin([90, np.nanmax(dec)])

# Turn on the dark mode
plt.style.use("dark_background")

# Make the ra and dec histograms
fig, ax = plt.subplots(2, 1, figsize=(6, 6))
fig.subplots_adjust(hspace=0.32, wspace=0.0)

ax[0].hist(ra, bins=100, range=(ra_min, ra_max), color="r", alpha=0.5)  # RA
ax[0].set_xlabel("RA [deg]")
ax[0].set_ylabel("Counts")
ax[0].grid()
ax[0].set_title(f"LEXI look direction RA for about {len(ra)} points")
ax[0].set_xlim(ra_min, ra_max)
ax[0].set_yscale("log")

ax[1].hist(dec, bins=100, range=(dec_min, dec_max), color="b", alpha=0.5)  # Dec
ax[1].set_xlabel("Dec [deg]")
ax[1].set_ylabel("Counts")
ax[1].grid()
ax[1].set_title(f"LEXI look direction Dec for about {len(dec)} points")
ax[1].set_xlim(dec_min, dec_max)
ax[1].set_yscale("log")
plt.savefig("../figures/ra_dec_hist.png")

plt.close()

# Plot 2d histogram of ra and dec with number of counts as the color
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
hb = ax.hexbin(ra, dec, gridsize=[360, 100], cmap="inferno", bins="log", mincnt=100)
ax.set_xlabel("RA [deg]")
ax.set_ylabel("Dec [deg]")
ax.grid()

cb = fig.colorbar(hb, ax=ax)
cb.set_label("Counts")
ax.set_xlim(275, 355)
ax.set_ylim(-50, 25)
plt.savefig("../figures/ra_dec_2d_hist.png")
