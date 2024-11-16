import cv2

# Data for this specific camera model.
camera_width = 1440
camera_height = 1080

class CameraController:
    def __init__(self, camera_index=1):
        self.cam = cv2.VideoCapture(camera_index)

    def is_opened(self):
        return self.cam.isOpened()

    def prepare_camera(self, height=camera_height, width=camera_width):
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def start(self):
        # Do nothing, this function is only here so
        # the switch from thorlabs camera to ltc is easier.
        pass

    def get_single_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            print("Error reading frame.")
            return None
        
        return frame
    
    def shutdown(self):
        self.cam.release()
