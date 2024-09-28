import numpy as np
import matplotlib.pyplot as plt

# Load the data from text files
max_val = np.loadtxt('max_val_arr.txt', delimiter=',', dtype=int)  # Load as integers
corr_dist = np.loadtxt('correction_dist_arr.txt', delimiter=',', dtype=int) # Load as floats

# bad_indexes = [95, 119, 183, 210, 223, 231, 250, 252, 285, 293]
# corr_dist[bad_indexes] = -250
#import ipdb; ipdb.set_trace()

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# Plot max_val in the first subplot
ax1.plot(np.arange(len(max_val)), max_val, color='b', marker='+')
ax1.set_title('Max Value per Frame')
ax1.set_xlabel('Frames')
ax1.set_ylabel('Max Value (int)')
ax1.grid()

# Plot corr_dist in the second subplot
ax2.plot(np.arange(len(corr_dist)), corr_dist, color='r', marker='o')
ax2.set_title('Correlation Distance per Frame')
ax2.set_xlabel('Frames')
ax2.set_ylabel('Correlation Distance (float)')
ax2.grid()

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()
