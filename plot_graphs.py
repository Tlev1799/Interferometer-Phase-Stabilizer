import numpy as np
import matplotlib.pyplot as plt

# Specify the filenames directly
filename = "pixles_error_with_correction_old.txt"
file2 = "pixles_error_no_correction_old.txt"


# Read the array from the text file
data = np.loadtxt(filename, delimiter=",")
data2 = np.loadtxt(file2)

# Create an x-axis representing the frames
# Assuming each array has the same number of rows (frames)
num_frames1 = data.shape[0]
frames1 = np.arange(1, num_frames1 + 1)

num_frames2 = data2.shape[0]
frames2 = np.arange(1, num_frames2 + 1)

frames = np.arange(1, 1000)


plt.plot(frames, data[:999], label="Stage Stabilizer On")
plt.plot(frames, data2[:999], label="Stage Stabilizer Off")
plt.title(f'Detected Error')
plt.xlabel('Frames')
plt.ylabel('Error [px]')
plt.grid()
plt.legend()

# Adjust layout
plt.tight_layout()
plt.show()
