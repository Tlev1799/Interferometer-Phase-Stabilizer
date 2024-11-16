from pyflycap2.interface import Camera
import cv2
import numpy as np
import time


width = 1600
height = 1200

cam = Camera(serial=17582932)

cam.connect()
cam.start_capture()

try:
    while True:
        cam.read_next_image()
        image_with_meta = cam.get_current_image()  # last image
        
        buffer = image_with_meta['buffer']
        image = np.frombuffer(buffer, dtype=np.uint8)
        image = image.reshape((height, width))
        
        cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
        cv2.imshow('Current frame', image)
                   
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        time.sleep(0.1)
        
except Exception as e:
    print(f"Received error: {e}")
    
finally:
    cam.disconnect()
    cv2.destroyAllWindows()