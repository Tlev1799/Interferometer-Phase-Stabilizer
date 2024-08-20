import numpy as np

def find_max_x_coordinate(frame):

    #print("Good, max finder was called")
    max_val = -1
    max_left_index = 0

    # Go over middle row
    #print("Getting middle frame")
    middle_row = frame[int(len(frame) / 2)]
    #print(f"middle row: {middle_row}")

    # NOTE: We want to find the longest streak of the maximum value.
    #print(f"Middle row index: {int(len(frame) / 2)}")
    for i, e in enumerate(middle_row):
        if max_val < e:
            #print(f"New max value: {e}")
            max_val = e
            max_left_index = i

    # Search for streaks of the max value and find the longest.
    max_streak_length = 0
    current_streak_length = 0
    is_in_streak = False
    margin = 2
    current_index = 0

    #print(f"max value is: {max_val}")
    for i, e in enumerate(middle_row):
        if e >= max_val - margin:
            if not is_in_streak:
                #print(f"Starting new streak at index: {i}")
                is_in_streak = True
                current_streak_length = 1
                current_index = i
            else:
                current_streak_length += 1
        elif is_in_streak:
            is_in_streak = False

            #print(f"Finishing new streak at index: {i}")
            if current_streak_length > max_streak_length:
                max_streak_length = current_streak_length
                max_left_index = current_index
                #print(f"New max streak found. len: {max_streak_length}, index: {max_left_index}")

    
    # If there are multiple instances of the max value, find the middle of it
    index = max_left_index
    while middle_row[index] == middle_row[index+1]:
        index += 1

    # NOTE: If there is an even amount of max value, the middle is of width 2 (2 pixels fit).
    # So the middle coordinate is exactly between them.
    max_coordinate = (max_left_index + index) / 2.0
    #print(f"max coordinate: {max_coordinate}")


    # return (middle_index, left_index, right_index) of the max value
    return max_coordinate, max_left_index, index


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
