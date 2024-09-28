import ipdb
import time
from pylablib.devices import Thorlabs


print("Setting up default capture")
cam = Thorlabs.ThorlabsTLCamera()
cam.setup_acquisition()
cam.start_acquisition()

val = []
for i in range(10):
    temp = cam.read_multiple_images()
    print("Attempt number {} received {} frames".format(i+1, len(temp)))
    val += temp
    time.sleep(0.1)
if 0 == len(val):
    print("No frames captured, restarting camera")

    print("Wait for 20 minuts.")
    time.sleep(60*20)
    cam.close()
    cam.open()
    cam.setup_acquisition()
    cam.start_acquisition()

print("Camera restarted, attemtpting reading again")
val = []
for i in range(10):
    temp = cam.read_multiple_images()
    print("Attempt number {} received {} frames".format(i+1, len(temp)))
    val += temp
    time.sleep(0.1)

if 0 == len(val):
    print("NOOO!")
else:
    print("YESSS!")

ipdb.set_trace()

