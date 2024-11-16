import cv2

# Constants for camera index and window name
CAMERA_INDEX = 1
WINDOW_NAME = 'Live Camera Feed'

# Open the camera at index 1
camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    print(f"Error: Could not open video source {CAMERA_INDEX}.")
else:
    # Set resolution (optional)
    FRAME_WIDTH = 1440
    FRAME_HEIGHT = 1080
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # Start a continuous loop to capture frames
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()

        if ret:
            # Display the captured frame
            cv2.imshow(WINDOW_NAME, frame)

            # Wait for 1 millisecond and break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error: Could not read frame.")
            break

    # Release the camera and close the window
    camera.release()
    cv2.destroyAllWindows()
