# TODO: Implement a function that receives a list of frames,
#       and returns a list of phases of the fringes in the frames.
#       For each frame return the unwrapped phase in the middle of the frame.

# TODO: This file should contain the main function.
#       - Initialize the camera and engine (engine is not implemented yet)
#       - Begin an enless loop of:
#           1) Read frames (the last 5 for example)
#           2) Get fringe phases from frames.
#           3) Calculate phase error direction (if we choose gradient descent algorithm)
#           4) Mathemtically translate phase error to distance to change.
#           5) Tell the engine how to move.

from camera_controller import CameraController
import numpy as np

def extract_phase(frames):
    phase = 0

    # TODO: Implement

    return phase

def adjust_engine(phases):
    """Adjust engine to fix phase

    Parameters
    ----------
    phases : _type_
        _description_
    """

    # TODO: Implement

def get_max(arr):
    max_val = arr[0][0]
    index = [0, 0]
    for i, a in enumerate(arr):
        for j, b in enumerate(a):
            if b > max_val:
                max_val = b
                index[0] = i
                index[1] = j

    return max_val, index

def find_min_index(frame):

    min_val = np.inf
    min_left_index = 0

    # Go over middle row
    middle_row = frame[len(frame[0]) / 2]
    for i, e in enumerate(middle_row):
        if min_val > e:
            min_val = e
            min_left_index = i
    
    # If there are multiple instances of the max value, find the middle of it
    index = min_left_index
    while middle_row[index] == middle_row[index+1]:
        index += 1

    # NOTE: If there is an even amount of min value, the middle is of width 2 (2 pixels fit).
    # This gives the left one.
    min_index = (min_left_index + index) / 2

    # return (middle_index, left_index, right_index) of the min value
    return min_index, min_left_index, index

def find_max_index(frame):

    max_val = -1
    max_left_index = 0

    # Go over middle row
    middle_row = frame[len(frame[0]) / 2]
    for i, e in enumerate(middle_row):
        if max_val < e:
            max_val = e
            max_left_index = i
    
    # If there are multiple instances of the max value, find the middle of it
    index = max_left_index
    while middle_row[index] == middle_row[index+1]:
        index += 1

    # NOTE: If there is an even amount of max value, the middle is of width 2 (2 pixels fit).
    # This gives the left one.
    max_index = (max_index + index) / 2

    # return (middle_index, left_index, right_index) of the max value
    return max_index, max_left_index, index

def extract_required_correction(frame, should_find_min=True):
    # Find min/max and calculate distance (in pixels) from the middle.
    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0

    if should_find_min:
        x, left_of_x, right_of_x = find_min_index(frame)
    else:
        x, left_of_x, right_of_x = find_max_index(frame)

   # 

    


    return distance


def main():
    # Connect to camera.
    cc = CameraController()

    # Prepare camera.
    cc.prepare_camera()

    # True for stabling destructive interference, false for instructive.
    stable_min = False

    try:
        while True:
            # Get the newest frame.
            frame = cc.capture_frames(1)
            distance = extract_required_correction(frame, should_find_min=stable_min)
            
    finally:
        cc.shutdown()


if __name__ == '__main__':
    main()
