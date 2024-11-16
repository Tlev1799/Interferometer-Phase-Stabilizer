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
  Then, after the program finished, run _plot_graphs.py_ file in _UTEM System_ folder (after updating the file paths there        too ofcourse)



  
