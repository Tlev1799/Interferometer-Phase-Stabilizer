# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 12:06:56 2024

@author: Laser
"""

import cv2
import time
import numpy as np
import traceback

from utils import find_max_x_coordinate, find_parabola_coefficients
from camera_controller import CameraController
from stage_controller import StageController

# Globals
g_relative_reference_x = 0
g_absolute_reference_x = 0
g_buffering_counter = 0
g_max_pixels_gap = 15

# Optimization parameters
g_deviation = 50
g_min_distance_fix = 0.5
g_max_distance_fix = 20
g_step_size = 0.2

# Collecting data
g_pixels_err = np.array([])


def run_stabilizer(camera_controller, stage_controller):
    # Prepare camera for capturing
    camera_controller.preapre_camera()
    
    cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
        
    while True:
        try:
            # Get next frame
            current_frame = camera_controller.get_next_frame()
            
            if current_frame.shape == (1200, 1600):
                # Display the frame on screen.
                cv2.imshow('Current frame', current_frame)
            else:
                print("Skipped an inconsistent frame")
            
            # Adjust stage according to the frame.
            adjust_stage(stage_controller, current_frame)
            
            # Pressing 'q' will terminate the window and exit the loop, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # NOTE: This can be changed according to system's requirements.
            time.sleep(0.005)
    
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            error_traceback = traceback.format_exc()
            
            print("Received an error!\n")
            print(f"Error type: {error_type}")
            print(f"Error message: {error_message}")
            print("Traceback:")
            print(error_traceback)
            
            # NOTE: For now ignore this error
            if "Image consistency error" not in error_message:
                break
            
        finally:
            file_path = "C:\\Users\\Laser\\OneDrive - Technion\\Documents\\Temp\\errors.txt"
            np.savetxt(file_path, g_pixels_err, fmt="%.6f", delimiter=",")
            
            
    camera_controller.close()
    cv2.destroyAllWindows()
        
def adjust_stage(stage_controller, frame):
    global g_absolute_reference_x
    global g_relative_reference_x
    global g_pixels_err
    global g_buffering_counter
    
    # Wait a few frames, making sure the image is stable.
    if 30 > g_buffering_counter:
        g_buffering_counter += 1
        return
    
    
    # Set reference values according to the 'first' frame.
    if 30 == g_buffering_counter:
        g_absolute_reference_x = int(find_max_x_coordinate(frame)[0])
        g_relative_reference_x = g_absolute_reference_x
        g_buffering_counter += 1
        return
    
    # Get distance of the constructive interference location from mid-frame, in pixels:
    distance = get_distance_from_reference(frame)
    
    # Make sure the error is in the fixable margin
    #print(f"Pixels distance: {distance}")
    abs_distance = np.abs(distance)
    if abs_distance < g_min_distance_fix or abs_distance > g_max_distance_fix:
        #print(f"Error is too small or too big: {distance}")
        return
    print(f"Pixels distance: {distance}")
    
    # If difference between frames is more than max_gap, do nothing.
    if len(g_pixels_err > 0) and np.abs(g_pixels_err[-1] - distance) > g_max_pixels_gap:
        # Probably a bug, ignore.
        return
    
    # Save next detected error.
    g_pixels_err = np.append(g_pixels_err, distance)
    
    # For 1 pixel fix, (13/20 [nm/px])

    adjusting_distance = 0
    # Convert from camera pixels to um of engine movement
    lamda = 800 * (10**-6) # mm
    D = 113 # pixels

    # For constructive interference (2*pi*n)
    converter = lamda/(4 * D) # [mm/px]
    adjusting_distance = (-1)*g_step_size*converter*distance # [mm]

    # Adjust engine.
    #print(f"distance to adjust: {adjusting_distance} [mm]")
    stage_controller.move_relative_mm(adjusting_distance)

def get_distance_from_reference(frame):
    global g_relative_reference_x

    # Trim frame only to close cols
    min_x = g_relative_reference_x - g_deviation
    max_x = g_relative_reference_x + g_deviation
    trimmed_frame = frame[:, min_x:max_x]
    
    # Find max x cooridnate in the trimmed area
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
        distance = g_absolute_reference_x - ((left_of_x + right_of_x) / 2)
    else:
        x_extrimum = -b1/(2*a1)
        distance = g_absolute_reference_x - x_extrimum
        
    # Update relative reference
    g_relative_reference_x = x  
    
    return distance

def main():
    # Connect to camera
    cam_ctl = CameraController(17582932)
    cam_ctl.connect()
    
    # Connect to stage
    stg_ctl = StageController()
    
    run_stabilizer(cam_ctl, stg_ctl)

if __name__ == '__main__':
    main()

