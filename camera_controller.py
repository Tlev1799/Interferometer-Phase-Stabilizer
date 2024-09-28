import time
import warnings
import numpy as np
from pylablib.devices import Thorlabs
from constants import TWENTY_MINUTES


class CameraController:
    def __init__(self):
        self.cam = None
        self.find_camera()

    def find_camera(self):
        """
        """
        serial_numbers = Thorlabs.list_cameras_tlcam()
        if 0 == len(serial_numbers):
            print("No cameras found")
            return
        
        cameras_amount, first_camera = len(serial_numbers), serial_numbers[0]
        print("Detected {} cameras".format(cameras_amount))
        
        print("Connecting to first camera, SN: {}".format(first_camera))
        self.cam = Thorlabs.ThorlabsTLCamera()
        print("Successfully connected!")

    def is_opened(self):
        return not self.cam

    def debug_prepare(self):
        self.cam.setup_acquisition()
        print("Camera may return None, check for it")

    def debug_get_frame(self):
         # Begin capture
        self.cam.start_acquisition()

        # Read frames
        frames = []
        while 0 == len(frames):
            frames = self.cam.read_multiple_images()
            print(len(frames))
            time.sleep(1)

        # Stop capture
        self.cam.stop_acquisition()

        # Return the only received frame
        import ipdb; ipdb.set_trace()
        return np.array(frames[0])


    def prepare_camera(self):
        self.cam.setup_acquisition()
        self.cam.start_acquisition()

        if self.is_capture_blocking():
            # This means the camera needs time to warm up...
            # I have absolutely no idea why this happens, the
            # ThorCam application seems to work just fine.
            warnings.warn("Initial capturing attempt has failed. \
                          The camera probably needs some time to warm up, \
                          this will take 20 minutes.")
            time.sleep(TWENTY_MINUTES)
            print("20 Minutes passed, reopening camera")

            self.restart_camera()


        print("Camera is ready!")

    def capture_frames(self, num_frames):
        # Begin capture
        self.cam.start_acquisition()

        # Read frames
        frames = []
        while len(frames) < num_frames:
            frames += self.cam.read_multiple_images()

        # Stop capture
        self.cam.stop_acquisition()

        # Return the last frames
        #import ipdb; ipdb.set_trace()
        return frames[-num_frames]
    
    def get_single_frame(self):
        frame = []
        while (frame is None) or (0 == len(frame)):
            # Only take the last frame received.
            frame = self.cam.read_multiple_images()

        # We only care about the recent one.
        return frame[-1]

    def begin_continous_capture(self):
        """_summary_
        """

        print("Setting up default capture configuration")
        self.cam.setup_acquisition()

        print("Attempting capture")
        self.cam.start_acquisition()

        if self.is_capture_blocking():
            # This means the camera needs time to warm up...
            # I have absolutely no idea why this happens, the
            # ThorCam application seems to work just fine.
            warnings.warn("Initial capturing attempt has failed. \
                          The camera probably needs some time to warm up, \
                          this will take 20 minutes.")
            time.sleep(TWENTY_MINUTES)
            print("20 Minutes passed, reopening camera")

            self.restart_camera()

    # def get_frames(self, num_frames):
    #     """_summary_

    #     Parameters
    #     ----------
    #     num_frames : _type_
    #         _description_

    #     Returns
    #     -------
    #     _type_
    #         _description_
    #     """
    #     frames = self.cam.read_multiple_images(rng=(0, num_frames))
    #     print("Requested {0} frames, read {1}".format(num_frames, len(frames)))
    #     return frames
    
    def start(self):
        """_summary_
        """
        self.cam.start_acquisition()

    def stop(self):
        """_summary_
        """
        self.cam.stop_acquisition()


    def shutdown(self):
        """_summary_
        """
        self.cam.close()

    def restart_camera(self, exposure_time=0.000005):
        """_summary_
        """
        self.cam.close()
        self.cam.open()
        self.cam.setup_acquisition()
        self.cam.set_exposure(exposure_time)
        print("All done, this should work :)")

    def is_capture_blocking(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        images = []

        # Attempt capturing 10 frames
        for _ in range(10):
            images += self.cam.read_multiple_images()
            time.sleep(0.1)

        return len(images) < 10
            
            







