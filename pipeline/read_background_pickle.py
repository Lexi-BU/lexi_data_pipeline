import glob
import pickle

import matplotlib.pyplot as plt
import numpy as np

folder = "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/background_files/pickle_files/5min_by_window/"

pickle_files = glob.glob(folder + "*.pkl")


for pickle_file in pickle_files:
    with open(pickle_file, "rb") as f:
        obj = pickle.load(f)
    background = obj["background"]
    ra_edges = obj["ra_edges"]
    dec_edges = obj["dec_edges"]
    ra_centers = obj["ra_center_map"]
    dec_centers = obj["dec_center_map"]

    plt.figure(figsize=(8, 6))
    plt.pcolormesh(
        ra_edges,
        dec_edges,
        background.T,
        shading="auto",
        cmap="plasma",
        norm=plt.Normalize(vmin=0, vmax=np.percentile(background, 99)),
    )
    plt.colorbar(label="Background (count/s/arcmin$^2$)")
    plt.xlabel("RA (deg)")
    plt.ylabel("Dec (deg)")
    plt.title("Sky Background")
    plt.gca().invert_xaxis()
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(pickle_file.replace(".pkl", ".png"), dpi=150)
    plt.close()
    print(f"Saved image for {pickle_file}")

    plt.figure(figsize=(8, 6))
    plt.pcolormesh(
        ra_centers,
        dec_centers,
        background.T,
        shading="auto",
        cmap="plasma",
        norm=plt.Normalize(vmin=0, vmax=np.percentile(background, 99)),
    )
    plt.colorbar(label="Background (count/s/arcmin$^2$)")
    plt.xlabel("RA (deg)")
    plt.ylabel("Dec (deg)")
    plt.title("Sky Background (centered)")
    plt.gca().invert_xaxis()
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(pickle_file.replace(".pkl", "_centered.png"), dpi=150)
    plt.close()
    print(f"Saved centered image for {pickle_file}")
