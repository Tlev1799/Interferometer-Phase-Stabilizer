# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 17:05:23 2024

@author: Laser
"""

from pyflycap2.interface import Camera
import numpy as np

class CameraController:
    def __init__(self, serial, width=1600, height=1200):
        self.cam = Camera(serial=serial)
        self.width = width
        self.height = height
        
    def connect(self):
        self.cam.connect()
        
    def preapre_camera(self):
        self.cam.start_capture()
       
    def get_next_frame(self):
        # Read the next frame
        self.cam.read_next_image()
        image_with_meta = self.cam.get_current_image()  # last image
        
        # Convert the buffer into np array.
        buffer = image_with_meta['buffer']
        image = np.frombuffer(buffer, dtype=np.uint8)
        
        return image.reshape((self.height, self.width))
     
    def close(self):
        self.cam.disconnect()
        