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

def adjust_engine(distance, k):
    # TODO: We need to choose a regularization parameter, and some
    # way to translate pixels into actual distance.
    # I thought something like
    #   1px = 0.5nm
    # for example, but that may be wrong if moving 1 pixel close to the middle,
    # is not the same as moving 1 pixel far from the middle, engine-wise.
    pass

def find_parabola_coefficients(coordinates):
    # Extract the coordinates.
    (x1, y1), (x2, y2), (x3, y3) = coordinates

    # Set up the system of equations.
    A = np.array([
        [x1**2, x1, 1],
        [x2**2, x2, 1],
        [x3**2, x3, 1]
    ])
    y = np.array([y1, y2, y3])

    # Solve for the coefficients a, b, c.
    return np.linalg.solve(A, y)


def find_min_x_coordinate(frame):

    min_val = np.inf
    min_left_index = 0

    # Find left most index of min value in middle row.
    middle_row = frame[len(frame[0]) / 2]
    for i, e in enumerate(middle_row):
        if min_val > e:
            min_val = e
            min_left_index = i
    
    # If there are multiple instances of the min value, find the middle of it.
    index = min_left_index
    while middle_row[index] == middle_row[index+1]:
        index += 1

    # NOTE: If there is an even amount of min value, the middle is of width 2 (2 pixels fit).
    # So the middle coordinate is exactly between them.
    min_coordinate = (min_left_index + index) / 2.0

    # return (middle_index, left_index, right_index) of the min value
    return min_coordinate, min_left_index, index

def find_max_x_coordinate(frame):

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
    # So the middle coordinate is exactly between them.
    max_coordinate = (max_left_index + index) / 2.0

    # return (middle_index, left_index, right_index) of the max value
    return max_coordinate, max_left_index, index

def extract_required_correction(frame, should_find_min=True):
    # Find min/max and calculate distance (in pixels) from the middle.
    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0
    middle_x_coordinate = (len(frame)/2) - 0.5

    if should_find_min:
        x, left_of_x, right_of_x = find_min_x_coordinate(frame)
    else:
        x, left_of_x, right_of_x = find_max_x_coordinate(frame)

    # Find real peak of the parabola.
    middle_row = frame[len(frame[0]) / 2]
    coordinates = [(x, middle_row[x]),
                   (left_of_x, middle_row[left_of_x]),
                   (right_of_x, middle_row[right_of_x])]
    a, b, c = find_parabola_coefficients(coordinates)

    x_extrimum = -b/(2*a)
    distance = middle_x_coordinate - x_extrimum

    # positive distance means we need to move right, negative means to move left.
    return distance


def main():
    # Connect to camera.
    cc = CameraController()

    # Prepare camera.
    cc.prepare_camera()

    # True for stabling destructive interference, false for instructive.
    stable_min = False

    # Size of each step in the gradient descent.
    k = 0.5

    try:
        while True:
            # Get the newest frame.
            frame = cc.capture_frames(1)
            distance = extract_required_correction(frame, should_find_min=stable_min)
            adjust_engine(distance, k)
            
    finally:
        cc.shutdown()


if __name__ == '__main__':
    main()
