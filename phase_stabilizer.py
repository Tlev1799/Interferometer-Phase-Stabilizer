from engine_controller import EngineController
from camera_controller import CameraController
from utils import find_min_x_coordinate, find_max_x_coordinate, find_parabola_coefficients
import cv2
import time
import threading
import numpy as np
import keyboard
import ipdb

lock = threading.Lock()
#engine_lock = threading.Lock()

# Global variables for communication between threads.
g_frame = None
g_step_size = 10**-9 # Step size of the feedback.
g_should_adjust = False
g_min_distance_fix = 30

# Counter for saving frames in files.
saved_frames_counter = 0

def get_distance_to_adjust(frame, should_find_min=False):
    # Find min/max and calculate distance (in pixels) from the middle.
    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0
    middle_x_coordinate = (len(frame)/2) - 0.5
    #print(f"middle coordinate: {middle_x_coordinate}")

    if should_find_min:
        #print("Finding min")
        return_tuple = find_min_x_coordinate(frame)
    else:
        #print("Finding max")
        return_tuple = find_max_x_coordinate(frame)

    x, left_of_x, right_of_x = [int(a) for a in return_tuple]
    #print(f"indexes: {left_of_x}, {x}, {right_of_x}")

    left_of_x -= 1
    right_of_x += 1

    # Find real peak of the parabola.
    middle_row = frame[int(len(frame[0]) / 2)]
    coordinates = [(x, middle_row[x]),
                   (left_of_x, middle_row[left_of_x]),
                   (right_of_x, middle_row[right_of_x])]
    a1, b1, c1 = find_parabola_coefficients(coordinates)

    if a1 == 0:
        distance = middle_x_coordinate - ((left_of_x + right_of_x) / 2)
    else:
        x_extrimum = -b1/(2*a1)
        distance = middle_x_coordinate - x_extrimum

    #print(f"maximum: {x_extrimum}")
    #print(f"distance: {distance}")

    # TODO: Distance now contains a value in pixels. We still need to convert it to nm for
    # the actual adjustment.

    # positive distance means we need to move right, negative means to move left.
    return distance


# Open camera, read and display images continously.
def camera_thread(cc):

    # Declare globals to be used.
    global g_frame

    try:
        # Prepare camera for contious capture.
        cc.prepare_camera()
        cc.start()

        while True:
            # Get last frame synchronously. 
            with lock:
                g_frame = cc.get_single_frame()
                if g_frame is None:
                    continue
                #g_frame = np.random.randint(0, 1024, (480, 640), dtype=np.uint16)

                g_frame = cv2.GaussianBlur(g_frame, (5, 5), 0)

                g_frame = cv2.medianBlur(g_frame, 3)

                # Convert the image to type that cv2 supports.
                #frame_uint8 = cv2.convertScaleAbs(g_frame, alpha=(255.0/65535.0))
                #normalized_frame = cv2.normalize(g_frame, None, 0, 255, cv2.NORM_MINMAX)
                g_frame = cv2.transpose(g_frame)
                frame_uint8 = (g_frame / 1023.0)*255
                

            # Note: Here we no longer use g_frame so we release the lock,
            #       holding it unecessarily will just slow us down.

            # Show the image on screen.
            cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
            cv2.imshow('Current frame', frame_uint8)

            # Pressing 'q' will terminate the window, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            #time.sleep(0.1)

    finally:
        cv2.destroyAllWindows()
        cc.shutdown()


# Continously calculate required engine adjustment.
def algorithm_thread(ec):

    # Declare globals to be used.
    global g_frame
    global g_step_size
    global g_should_adjust
    global g_min_distance_fix

    #index = 0
    debug_counter = 1
    file_name_counter = 0
    while True:
        # Save the current frame.
        with lock:
            if g_frame is None:
                time.sleep(0.1)
                continue
            frame = g_frame.copy()
            #np.savetxt(f"temp\\file number {index}", frame, delimiter=',', fmt='%d')
            #index += 1

            # Adjust the engine accordingly.
            if g_should_adjust:
                distance = get_distance_to_adjust(frame, should_find_min=False)
                with open(f"debug\\debug_text{file_name_counter}.txt", "a") as f:
                    f.write(f"frame: {frame}\n\nFound max at: {((len(frame)/2) - 0.5) - distance}\nDistance to middle: {distance}\n\n\n")
                debug_counter += 1
                if 0 == debug_counter % 100:
                    debug_counter = 1
                    file_name_counter += 1
                
                #print(f"Distance calculated {distance}")
                if np.abs(distance) > g_min_distance_fix:
                    ec.move_engine(g_step_size*distance)

        # Wait for 100ms to let g_frame time to update in the other thread.
        time.sleep(0.1)


def set_feedback_step_size():
    try:
        new_k = float(input("Enter new value for size step"))

        if new_k <= 0 or new_k >= 1:
            print("ERROR: K must satisfy: 0 < k < 1")
            return
        
        # Update k synchorniously
        with lock:
            g_step_size = new_k

    except ValueError:
        print("Invalid value for k")


def manual_adjust(cc, ec):

    # Stop capturing and adjusting using the lock on g_frame
    with lock:
        while True:
            try:
                # Manually adjsut distance.
                distance = float(input("Enter distance to adjust: "))
                ec.move_engine(g_step_size*distance)

                # Display updated frame for 1 second.
                time.sleep(0.01)
                frame = cc.get_single_frame()
                frame_uint8 = (frame / 1023.0)*255
                cv2.namedWindow('Debug adjsuted frame', cv2.WINDOW_NORMAL)
                cv2.imshow('Debug adjsuted frame', frame_uint8)
                cv2.waitKey(1000)

            except ValueError:
                print("Not a valid float")
            except Exception as e:
                print(f"Some error occurred: {e}, try again")

            finally:
                string = input("Make another adjsutment? (y/n): ")
                if 'n' == string[0]:
                    break

def display_distance():
    try:
        with lock:
            frame = g_frame.copy()
            print("Calling get_distance")
            distance = get_distance_to_adjust(frame, should_find_min=False)
            print(f"Distance for current frame: {distance}")
            input("Press Enter to continue")
    except Exception as e:
        print(f"Some error occurred: {e}")

def pdb(cc, ec):
    with lock:
        ipdb.set_trace()

def set_exposure_time(cc):
    try:
        exposure_time = float(input("Enter new exposure time: "))
        with lock:
            cc.cam.set_exposure(exposure_time)
            print(f"Successfully set exposure time to: {exposure_time}")
    except ValueError:
        print("Invalid value")
    except Exception as e:
        print(f"Some error occurred: {e}")

def pause_resume_engine():
    #import ipdb; ipdb.set_trace()
    global g_should_adjust
    with lock:
        g_should_adjust = not g_should_adjust


def save_frame_in_file():
    global saved_frames_counter
    with lock:
        np.savetxt(f"temp\\file number {saved_frames_counter}", g_frame, delimiter=',', fmt='%d')
        saved_frames_counter += 1

def control_engine(ec):
    try:
        value = float(input("Enter value to adjust: "))
        ec.move_engine(value)
    except ValueError:
        print("Invalid value for distance")


def set_min_distance():
    global g_min_distance_fix

    try:
        val = float(input("Enter new min distance to fix: "))
    except ValueError as e:
        print(f"Invalid value received, {e}")
        return

    with lock:
        g_min_distance_fix = val

def debug_thread(cc, ec):
    
    # Declare globals to be used.
    global g_frame
    global g_step_size
    global g_should_adjust

    # For manually adjusting engine.
    keyboard.add_hotkey('a', manual_adjust, args=(cc, ec))

    # Change step size (value of k)
    keyboard.add_hotkey('k', set_feedback_step_size)

    # Display calculated distance to adjust for the current frame.
    keyboard.add_hotkey('d', display_distance)

    # Set exposure time.
    keyboard.add_hotkey('x', set_exposure_time, args=(cc, ))

    # Pause/resume adjusting algorithm.
    keyboard.add_hotkey('p', pause_resume_engine)

    # Set break point (Blocks camera footage !)
    keyboard.add_hotkey('b', pdb, args=(cc, ec))

    keyboard.add_hotkey('s', save_frame_in_file)

    keyboard.add_hotkey('z', control_engine, args=(ec, ))

    keyboard.add_hotkey('m', set_min_distance)

    # Wait forever for different keys. 'e' will exit the debug thread. 
    keyboard.wait('e')


def main():

    # Connect to camera.
    #cc = None
    cc = CameraController()
    if not cc.cam:
        exit()

    # Connect to engine..
    ec = None
    try:
        pass
        ec = EngineController()
        ec.connect()
    except:
        print("Error connecting to engine, exiting")
        exit()

    # Start capturing frames in a new thread.
    cam_thread = threading.Thread(target=camera_thread, args=(cc,), daemon=True)
    cam_thread.start()

    global g_frame
    while g_frame is None:
        time.sleep(0.1)

    # Begin loop of debug thread.
    dbg_thread = threading.Thread(target=debug_thread, args=(cc, ec), daemon=True)
    dbg_thread.start()

    # Camera is being run in the second thread, we are the algorithm thread.
    algorithm_thread(ec)


if __name__ == '__main__':
    main()
