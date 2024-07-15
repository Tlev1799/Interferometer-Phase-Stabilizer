import time
import warnings
from pylablib.devices import Thorlabs
from constants import TWENTY_MINUTES


print("BLAHHHHHHHHHHHH")
class camera_controller:
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
        print("Detected {} cameras.", cameras_amount)
        
        print("Connecting to first camera, SN: {}".format(first_camera))
        self.cam = Thorlabs.ThorlabsTLCamera()
        print("Successfully connected!")

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

    def get_frames(self, num_frames):
        """_summary_

        Parameters
        ----------
        num_frames : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        frames = self.cam.read_multiple_images(rng=(0, num_frames))
        print("Requested {0} frames, read {1}".format(num_frames, len(frames)))
        return frames
    
    def shutdown(self):
        """_summary_
        """
        #self.cam.stop_acquisition()
        self.cam.close()

    def restart_camera(self):
        """_summary_
        """
        self.cam.close()
        self.cam.open()
        self.cam.setup_acquisition()
        self.cam.start_acquisition()
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
            
            







