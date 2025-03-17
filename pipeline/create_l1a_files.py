import glob
import importlib
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import get_l1a_files as glf
import numpy as np
import pandas as pd
from tqdm import tqdm

importlib.reload(glf)

start = time.time()
file_data_folder = (
    "/home/cephadrius/Desktop/git/Lexi-BU/lexi_data_pipeline/data/level_0/2025-03-16/"
)

# Get the list of files in the folder and subfolders
file_val_list = sorted(glob.glob(str(file_data_folder) + "/*.dat", recursive=True))

# Randomly select 100 files for testing
# define a random seed
# np.random.seed(42)
# selected_file_val_list = np.random.choice(file_val_list, size=100, replace=False)

# Determine number of CPU cores and allocate 90%
total_cores = multiprocessing.cpu_count()
num_workers = max(1, int(total_cores * 0.9))  # Ensure at least 1 worker


# Function to process each file
def process_file(file_val):
    return glf.read_binary_file(file_val=file_val)


results = []
# Parallel processing
with ProcessPoolExecutor(max_workers=num_workers) as executor:
    # Submit all tasks
    future_to_file = {executor.submit(process_file, file): file for file in file_val_list}

    # Wrap as_completed() with tqdm for progress tracking
    for future in tqdm(
        as_completed(future_to_file),
        total=len(file_val_list),
        desc="Processing Files",
        unit="file",
    ):
        results.append(future.result())
# Extract results if needed
for file_name, df_sci, df_hk, sci_save_filename, hk_save_filename in results:
    pass  # Process further if required

# Print the time taken
end = time.time()
print(f"Time taken: {end - start:.2f} seconds")
