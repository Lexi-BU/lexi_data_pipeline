import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

offset_1 = 1
offset_2 = 2
offset_3 = 3
offset_4 = 4

# Create a random set of numbers between 1 and 4.51 of length 1000
np.random.seed(0)
channel1 = np.random.uniform(1, 4.51, 1000)
np.random.seed(1)
channel2 = np.random.uniform(1, 4.51, 1000)

ratio_1 = channel1 / (channel2 + channel1)
ratio_2 = (channel1 - offset_1) / (channel2 - offset_2 + channel1 - offset_1)
ratio_3 = (channel1 - offset_3) / (channel2 - offset_4 + channel1 - offset_3)

# Find the difference between ratio_2 and ratio_3
diff_ratio_2_3 = ratio_2 - ratio_3
# plot the three ratios
plt.figure()
plt.scatter(range(len(ratio_1)), diff_ratio_2_3 * 100 / ratio_2, label="ratio_1")
plt.legend()
plt.savefig("ratio_plot.png")
plt.show()
