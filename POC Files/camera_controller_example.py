import time
from pylablib.devices import Thorlabs

# Find camera
serial_numbers = Thorlabs.list_cameras_tlcam()
if 0 == len(serial_numbers):
    print("No cameras found")
    exit()

# Connect to camera
first_camera = serial_numbers[0]
print("Connecting to first camera, SN: {}".format(first_camera))
cam = Thorlabs.ThorlabsTLCamera()
cam.setup_acquisition()
cam.start_acquisition()

# Here I try to start reading frames.
images = []
for _ in range(10):
    images += cam.read_multiple_images()
    time.sleep(0.1)

print(f"Before waiting: {len(images)}")

# Now, we wait 20 minutes
time.sleep(20*60)

# Try again
images = []
for _ in range(10):
    images += cam.read_multiple_images()
    time.sleep(0.1)

print(f"After waiting, before restart: {len(images)}")

# reopen the camera
cam.close()
cam.open()
cam.setup_acquisition()
cam.start_acquisition()

# One last time.
images = []
for _ in range(10):
    images += cam.read_multiple_images()
    time.sleep(0.1)

print(f"After restart: {len(images)}")
