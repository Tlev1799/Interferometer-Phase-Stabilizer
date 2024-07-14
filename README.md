
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




