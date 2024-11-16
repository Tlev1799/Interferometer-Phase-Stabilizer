Requirements for running UTEM system stabilizer:
  Install the following python libraries (run the commands):
  Camera interface: "pip install pyflycap2"
  Stage interface: "pip install newportxps"

  Standard libraries required:
  numpy, matplotlib, opencv-python.


How to run:
  After everything is installed, open and run _stabilizer.py_ in UTEM System folder in 
  a computer that's connected to the stage and camera _(UTEM System\camera_controller.py)_.

  For stage, if the default IP isn't right, add the host parameter when creating the object in main.
  Also, change the group name if needed _(UTEM System\stage_controller.py)_.

  For camera, change serial number, width and height parameters to the ones specific for your camera.

Plotting results:
  Before running, update the path to save the text files to (in _stabilizer.py_ file, inside _finally_ statement)
  Then, after the program finished, run _plot_graphs.py_ file in _UTEM System_ folder (after updating the file paths there     too ofcourse)




















We used python 3.12.4, which is currently the newest (July 2024).
Firstly, install the required python libraries by running the following command:
_pip install pylablib ftd2xx_

We used Thorlabs scientific camera model CS165MU, install Thorcam here:
https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam

pylablib implements APIs for many USB devices (https://pylablib.readthedocs.io/en/latest/),
and it has a specific API for Thorlabs scientific camera, which wraps the 
designed software interface officially provided by Thorlabs.

Also required, is FTDI-driver, which contains some dlls needed by pylablib,
install here: https://ftdichip.com/drivers/
guidlines: https://ftdichip.com/document/installation-guides/

NOTE: The only dll file that was really needed is ftd2xx.dll
and it is needed to be pasted in one of Windows' dll paths (like "C:\Windows\System32", "C:\Windows\SysWOW64").

We had an issue that pylablib searched for ftd2xx.dll, not ftd2xx64.dll, but required the 64-bit file 
to run properly, so we removed the "64" from ftd2xx64.dll file name and placed it in System32 - and that worked :)

