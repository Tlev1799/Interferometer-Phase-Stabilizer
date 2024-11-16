# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 17:07:18 2024

@author: Laser
"""

import numpy as np
import matplotlib.pyplot as plt

file_path = "C:\\Users\\Laser\\OneDrive - Technion\\Documents\\Temp\\errors_pixels_stabilizer_off.txt"
window_size = 25

data = np.loadtxt(file_path, delimiter=",")
smoothed_data = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
plt.plot(data)
plt.xlabel("Frames")
plt.ylabel("Error [px]") 
plt.show()