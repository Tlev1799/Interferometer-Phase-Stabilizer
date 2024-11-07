from camera_controller_UTEM import FLIRCapture
import matplotlib as plt

# Instantiate and configure the camera
flir = FLIRCapture()
flir.connect()
flir.configure_camera()
flir.start_acquisition()

# Set up the display
plt.ion()  # Enable interactive mode for real-time updating
fig, ax = plt.subplots()
image_display = None

# Capture and display frames in a loop
try:
    for jj in range(200):
        frame = flir.capture_frame()
        if frame is not None:
            if image_display is None:
                # Initialize the image display with the first frame
                image_display = ax.imshow(frame, cmap='gray', vmin=0, vmax=255)
                plt.axis("off")
            else:
                # Update the image data
                image_display.set_data(frame)
            plt.draw()
            plt.pause(0.01)  # Short pause for display update
except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    # Clean up
    flir.stop_acquisition()
    flir.disconnect()
    plt.ioff()  # Disable interactive mode
    plt.show()