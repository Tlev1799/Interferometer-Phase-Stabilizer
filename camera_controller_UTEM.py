import pyspin

# TODO: Either install FLIR driver and setup SDK package, or run the code on their computer.

class FLIRCapture:
    def __init__(self):
        self.system = pyspin.System.GetInstance()
        self.camera = None

    def connect(self):
        """Initialize and connect to the camera."""
        cam_list = self.system.GetCameras()
        if cam_list.GetSize() == 0:
            cam_list.Clear()
            self.system.ReleaseInstance()
            raise Exception("No FLIR cameras detected.")

        # Select the first camera (assumed to be deviceID 1)
        self.camera = cam_list[0]
        self.camera.Init()
        print("Camera connected.")

    def configure_camera(self):
        """Configure camera settings."""
        # Set acquisition mode to single frame (FramesPerTrigger equivalent)
        self.camera.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)

        # Set camera to manual exposure
        self.camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.camera.ExposureMode.SetValue(PySpin.ExposureMode_Manual)

        # Set other manual modes if available
        if PySpin.GainAuto_Off in self.camera.GainAuto.GetAccessMode():
            self.camera.GainAuto.SetValue(PySpin.GainAuto_Off)
        if PySpin.ShutterMode in self.camera.ShutterMode.GetAccessMode():
            self.camera.ShutterMode.SetValue(PySpin.ShutterMode_Manual)

        # Configure frame rate mode and strobe if applicable
        if PySpin.FrameRateAuto_Off in self.camera.FrameRateAuto.GetAccessMode():
            self.camera.FrameRateAuto.SetValue(PySpin.FrameRateAuto_Off)
        if PySpin.StrobeMode_On in self.camera.Strobe1.GetAccessMode():
            self.camera.Strobe1.SetValue(PySpin.StrobeMode_On)
        
        print("Camera configured with manual settings.")

    def capture_image(self):
        """Capture a single frame."""
        self.camera.BeginAcquisition()
        image_result = self.camera.GetNextImage()

        if image_result.IsIncomplete():
            print("Image incomplete with image status %d ..." % image_result.GetImageStatus())
            image_result.Release()
            return None

        # Convert the image to numpy array if needed
        image_data = image_result.GetNDArray()
        image_result.Release()
        print("Image captured.")
        return image_data

    def disconnect(self):
        """Disconnect and clean up."""
        if self.camera is not None:
            self.camera.EndAcquisition()
            self.camera.DeInit()
            self.camera = None
        self.system.ReleaseInstance()
        print("Camera disconnected.")

# Example usage:
# flir = FLIRCapture()
# flir.connect()
# flir.configure_camera()
# img = flir.capture_image()
# flir.disconnect()