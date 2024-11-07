#from ltc_camera_controller import CameraController
#from engine_controller import EngineController
from camera_controller_UTEM import FLIRCapture
from engine_controller_xps import XPSController
from utils import find_min_x_coordinate, find_max_x_coordinate, find_parabola_coefficients

import numpy as np
import time
import cv2
import sys


# Engine parameters
g_engine_acc = 1 # mm/s^2
g_engine_vel = 2 * (10**-3) # mm/s
g_engine_axis = 1 # Unitless

# Step size of Gradient Descent algorithm.
g_step_size = 0.1 # Unitless

# First frame max value coord
g_first_frame_max_x = 0
g_is_first_frame = True

# Bounds beyond which the algorithm will not adjust the engine.
# Lower bound is to avoid constanly jumping when disturbances are very small.
# Upper bound is to ignore single frame errors.
g_min_distance_fix = 0 # Camera pixels
g_max_distance_fix = 300 # Camera pixels

# Data collection for graphs (per frame).
g_camera_mid_frame = (360, 640) # Integers, (x, y) of middle of frame. Constant for each camera.
g_max_values = np.array([]) # Floats
g_max_value_x_coordinate = np.array([]) # Integers
g_engine_adjusting_distances = np.array([]) # Floats, in nm
g_pixels_error = np.array([]) # integers, in pixels
g_last_frame = None # Copy of the final frame, will be saved to file.

# Last reference.
g_reference_x0 = 0
g_reference_relative = 0
g_deviation = 35


def run_stabilizer(camera_controller, engine_controller):
    global g_first_frame_max_x

    current_frame = None

    # Everything will be in try-except so it never crashes.
    try:
        camera_controller.configure_camera()
        camera_controller.start_acquisition()
        # Prepare camera for capturing frames.
        # camera_controller.prepare_camera()
        # camera_controller.start()

        # Begine the feedback loop
        while True:
            # Read a single frame.
            #current_frame = camera_controller.get_single_frame()
            current_frame = camera_controller.capture_frame()
            if current_frame is None:
                time.sleep(0.01)
                continue

            # This specific camera is colored, convert it to gray scale.
            current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # Display the frame on screen.
            cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
            cv2.imshow('Current frame', current_frame)

            # Adjust engine according to the frame.
            adjust_engine(engine_controller, current_frame)

            # Pressing 'q' will terminate the window and exit the loop, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        exc_info = sys.exc_info()
        print(f"Error occurred: {e}")
    finally:
        camera_controller.stop_acquisition()
        camera_controller.disconnect()
        #camera_controller.shutdown()
        #engine_controller.close()

        # Save data for debugging.
        if current_frame is not None:
            print(len(current_frame[0]))
            print(len(current_frame))
            np.savetxt("last_frame.txt", current_frame, fmt="%d", delimiter=",")
        save_graphs_data()


def save_graphs_data():
    np.savetxt("max_value.txt", g_max_values, fmt="%.6f", delimiter=",")
    np.savetxt("x_coordinate.txt", g_max_value_x_coordinate, fmt="%d", delimiter=",")
    np.savetxt("adjusting_dists.txt", g_engine_adjusting_distances, fmt="%.6f", delimiter=",")
    #np.savetxt("pixles_error_with_correction.txt", g_pixels_error, fmt="%d", delimiter=",")
    np.savetxt("pixles_error_no_correction.txt", g_pixels_error, fmt="%d", delimiter=",")



def adjust_engine(engine_controller, frame):
    global g_engine_adjusting_distances 
    global g_first_frame_max_x   
    global g_is_first_frame 
    global g_pixels_error      

    if g_is_first_frame:
        distance, x = get_distance_from_mid(frame, should_find_min=False)
        g_first_frame_max_x = x
        g_is_first_frame = False
        return

    # Get distance of the constructive interference location from mid-frame, in pixels:
    distance = get_distance_from_x(frame, should_find_min=False)
    g_pixels_error = np.append(g_pixels_error, distance)

    # Make sure the error is in the fixable margin
    abs_distance = np.abs(distance)
    if abs_distance < g_min_distance_fix or abs_distance > g_max_distance_fix:
        print(f"Error is too small or too big: {distance}")
        return

    adjusting_distance = 0
    # Convert from camera pixels to um of engine movement
    # TODO: Implement...
    lamda = 633 * (10**-6) # mm
    D = 140 # pixels

    # For constructive interference (2*pi*n)
    converter = lamda/(4 * D) # [mm/px]
    adjusting_distance = (-1)*g_step_size*converter*distance # [mm]

    # Adjust engine.
    #engine_controller.move_engine(distance=adjusting_distance)
    engine_controller.move_engine(adjusting_distance)

    # Save data for later graphs.
    g_engine_adjusting_distances = np.append(g_engine_adjusting_distances, adjusting_distance)
    

def get_distance_from_x(frame, should_find_min=False):
    global g_max_value_x_coordinate
    global g_max_values
    global g_reference_relative

    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0

    # Trim frame to desired search area
    min_x = g_reference_relative-g_deviation
    max_x = g_reference_relative+g_deviation
    trimmed_frame = frame[:, min_x:max_x]

    # Find min/max x coordinate in the middle row.
    if should_find_min:
        return_tuple = find_min_x_coordinate(trimmed_frame)
    else:
        return_tuple = find_max_x_coordinate(trimmed_frame)

    # Round to integers, giving the start and end of the max/min sequences.
    x, left_of_x, right_of_x = [int(a) for a in return_tuple]
    left_of_x -= 1
    right_of_x += 1

    # Update coordinates back to original frame
    x += min_x
    left_of_x += min_x
    right_of_x += min_x

    # Find real peak of the parabola.
    middle_row = frame[int(len(frame[0]) / 2)]
    coordinates = [(x, middle_row[x]),
                   (left_of_x, middle_row[left_of_x]),
                   (right_of_x, middle_row[right_of_x])]
    a1, b1, c1 = find_parabola_coefficients(coordinates)

    # Handle special case where the parabole is a straight line.
    if np.abs(a1) < 0.001:
        distance = g_reference_x0 - ((left_of_x + right_of_x) / 2)
    else:
        x_extrimum = -b1/(2*a1)
        distance = g_reference_x0 - x_extrimum

    # Save max value for drawing graphs.
    g_max_value_x_coordinate = np.append(g_max_value_x_coordinate, x)
    g_max_values = np.append(g_max_values, middle_row[x])

    g_reference_relative = x

    # positive distance means we need to move right, negative means to move left.
    return distance


def get_distance_from_mid(frame, should_find_min=False):
    global g_max_value_x_coordinate
    global g_max_values
    global g_reference_x0
    global g_reference_relative

    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0
    middle_x_coordinate = (len(frame[0])/2) - 0.5

    # Find min/max x coordinate in the middle row.
    if should_find_min:
        return_tuple = find_min_x_coordinate(frame)
    else:
        return_tuple = find_max_x_coordinate(frame)

    # Round to integers, giving the start and end of the max/min sequences.
    x, left_of_x, right_of_x = [int(a) for a in return_tuple]
    left_of_x -= 1
    right_of_x += 1

    # Find real peak of the parabola.
    middle_row = frame[int(len(frame[0]) / 2)]
    coordinates = [(x, middle_row[x]),
                   (left_of_x, middle_row[left_of_x]),
                   (right_of_x, middle_row[right_of_x])]
    a1, b1, c1 = find_parabola_coefficients(coordinates)

    # Handle special case where the parabole is a straight line.
    if np.abs(a1) < 0.001:
        distance = middle_x_coordinate - ((left_of_x + right_of_x) / 2)
    else:
        x_extrimum = -b1/(2*a1)
        distance = middle_x_coordinate - x_extrimum

    # Save max value for drawing graphs.
    g_max_value_x_coordinate = np.append(g_max_value_x_coordinate, x)
    g_max_values = np.append(g_max_values, middle_row[x])

    g_reference_x0 = x
    g_reference_relative = x

    # positive distance means we need to move right, negative means to move left.
    return distance, x


def main():
    # Connect to camera.
    # cc = CameraController()
    # if not cc.is_opened():
    #     print("Failed opening camera, exiting...")
    #     exit()

    # Instantiate and configure the camera
    cc = FLIRCapture()
    cc.connect()

    # Connect to engine.
    ec = None
    try:
        # ec = EngineController()
        # NOTE: For now default username and password.
        ec = XPSController('some IP here !!!')
        ec.connect()
        # ec.prepare_engine(g_engine_axis, g_engine_acc, g_engine_vel)
        # ec.get_movement_data()

    except Exception as e:
        print(f"Error connecting to engine: {e}")
        print("Exiting...")
        exit()

    # Initiate the phase stabilizer.
    run_stabilizer(cc, ec)


if __name__ == '__main__':
    main()
