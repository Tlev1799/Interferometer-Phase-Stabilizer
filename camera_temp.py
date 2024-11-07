from ltc_camera_controller import CameraController

import time
import cv2


def run_stabilizer(camera_controller):
    current_frame = None

    # Everything will be in try-except so it never crashes.
    try:
        # Prepare camera for capturing frames.
        camera_controller.prepare_camera()
        camera_controller.start()

        # Begine the feedback loop
        while True:
            # Read a single frame.
            current_frame = camera_controller.get_single_frame()
            if current_frame is None:
                time.sleep(0.01)
                continue

            # This specific camera is colored, convert it to gray scale.
            current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Display the frame on screen.
            cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
            cv2.imshow('Current frame', current_frame)

            # Pressing 'q' will terminate the window and exit the loop, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        camera_controller.shutdown()


def main():
    # Connect to camera.
    cc = CameraController()
    if not cc.is_opened():
        print("Failed opening camera, exiting...")
        exit()

    # Initiate the phase stabilizer.
    run_stabilizer(cc)
    

if __name__ == '__main__':
    main()
