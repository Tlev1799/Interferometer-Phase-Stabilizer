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

def main():
    # Connect to camera and begin capture.
    cc = CameraController()
    cc.begin_continous_capture()

    # Amount of frames required for a single phase to be extracted.
    frames_per_phase = 10

    # Amount of phases required to decide the next engine correction.
    phases_per_correction = 2

    frames = []
    phases = []

    # Start reading_frames contoniously
    try:
        while True:
            frame = cc.get_frames(1)
            print("Got {} frame".format(len(frame)))
            value, index = get_max(frame)

            print("max value was found at {0} and its: {1}", index, value)
            # frames += cc.get_frames(frames_per_phase)
            # if len(frames) >= frames_per_phase:
            #     print("Captured {0} frames, extracting phase")
            #     phases += extract_phase(frames)

            #     if len(phases) >= phases_per_correction:
            #         print("Extracted {0} phases, adjusting engine")
            #         adjust_engine(phases)

    finally:
        cc.shutdown()


if __name__ == '__main__':
    main()
