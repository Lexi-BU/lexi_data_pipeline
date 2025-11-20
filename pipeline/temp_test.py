import numpy as np
import tabulate
from spacepy.pycdf import CDF as cdf

file_name = (
    "/mnt/cephadrius/bu_research/lexi_data/l2/5min/clps-bgm1_lexi_l2-images_202503161905_V0.cdf"
)
dat = cdf(file_name)

cosmic_background_map = np.asarray(dat["cosmic_background_map"][...])[0]
dark_background_map = np.asarray(dat["dark_background_map"][...])[0]
total_background_map = np.asarray(dat["total_background_map"][...])[0]
lexi_image = np.asarray(dat["lexi_image"][...])[0]
lexi_image_background_corrected = np.asarray(dat["lexi_image_background_corrected"][...])[0]
lexi_image_background_flatfield_corrected = np.asarray(
    dat["lexi_image_background_flatfield_corrected"][...]
)[0]
fill_value = -1e31
cosmic_background_map[cosmic_background_map == fill_value] = np.nan
dark_background_map[dark_background_map == fill_value] = np.nan
total_background_map[total_background_map == fill_value] = np.nan
lexi_image[lexi_image == fill_value] = np.nan
lexi_image_background_corrected[lexi_image_background_corrected == fill_value] = np.nan
lexi_image_background_flatfield_corrected[
    lexi_image_background_flatfield_corrected == fill_value
] = np.nan

print(f"Loaded CDF file: {file_name}")
# Print the statistics of all the maps in a table
headers = ["Map", "Mean", "Median", "Std Dev", "Min", "Max"]
table = [
    [
        "Cosmic Background Map",
        np.nanmean(cosmic_background_map),
        np.nanmedian(cosmic_background_map),
        np.nanstd(cosmic_background_map),
        np.nanmin(cosmic_background_map),
        np.nanmax(cosmic_background_map),
    ],
    [
        "Dark Background Map",
        np.nanmean(dark_background_map),
        np.nanmedian(dark_background_map),
        np.nanstd(dark_background_map),
        np.nanmin(dark_background_map),
        np.nanmax(dark_background_map),
    ],
    [
        "Total Background Map",
        np.nanmean(total_background_map),
        np.nanmedian(total_background_map),
        np.nanstd(total_background_map),
        np.nanmin(total_background_map),
        np.nanmax(total_background_map),
    ],
]

# Print the table
print(tabulate.tabulate(table, headers=headers))

print("\n\n")
# Print new table for lexi images
headers = ["Map", "Mean", "Median", "Std Dev", "Min", "Max"]
table = [
    [
        "Lexi Image",
        np.nanmean(lexi_image),
        np.nanmedian(lexi_image),
        np.nanstd(lexi_image),
        np.nanmin(lexi_image),
        np.nanmax(lexi_image),
    ],
    [
        "BG Corrected",
        np.nanmean(lexi_image_background_corrected),
        np.nanmedian(lexi_image_background_corrected),
        np.nanstd(lexi_image_background_corrected),
        np.nanmin(lexi_image_background_corrected),
        np.nanmax(lexi_image_background_corrected),
    ],
    [
        "BG F Corrected",
        np.nanmean(lexi_image_background_flatfield_corrected),
        np.nanmedian(lexi_image_background_flatfield_corrected),
        np.nanstd(lexi_image_background_flatfield_corrected),
        np.nanmin(lexi_image_background_flatfield_corrected),
        np.nanmax(lexi_image_background_flatfield_corrected),
    ],
]

# Print the table
print(tabulate.tabulate(table, headers=headers))
