from engine_controller import EngineController
from ltc_camera_controller import CameraController
from utils import find_min_x_coordinate, find_max_x_coordinate, find_parabola_coefficients
import cv2
import time
import threading
import numpy as np
from graphs import Graphs as gr
from scipy.ndimage import rotate

lock = threading.Lock()

# Global variables for communication between threads.
g_frame = None
g_step_size = 0.5 # Step size of the feedback.
g_should_adjust = True
g_min_distance_fix = 20
g_max_distance_fix = 300
g_max_val_coord_X = np.array([])
g_not_saved = True

g_distances = np.array([])
g_dist_not_saved = True

# Counter for saving frames in files.
saved_frames_counter = 0

def get_distance_to_adjust(frame, should_find_min=False):
    global g_max_val_coord_X
    global g_not_saved

    # Find min/max and calculate distance (in pixels) from the middle.
    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0
    middle_x_coordinate = (len(frame[0])/2) - 0.5

    if should_find_min:
        return_tuple = find_min_x_coordinate(frame)
    else:
        return_tuple = find_max_x_coordinate(frame)

    x, left_of_x, right_of_x = [int(a) for a in return_tuple]
    if len(g_max_val_coord_X) < 1000:
        g_max_val_coord_X = np.append(g_max_val_coord_X, x)
    elif g_not_saved:
        np.savetxt("X_coord.txt", g_max_val_coord_X, delimiter = ',', fmt="%d")
        g_not_saved = False

    
    left_of_x -= 1
    right_of_x += 1

    # Find real peak of the parabola.
    middle_row = frame[int(len(frame[0]) / 2)]
    coordinates = [(x, middle_row[x]),
                   (left_of_x, middle_row[left_of_x]),
                   (right_of_x, middle_row[right_of_x])]
    a1, b1, c1 = find_parabola_coefficients(coordinates)

    if np.abs(a1) < 0.001:
        distance = middle_x_coordinate - ((left_of_x + right_of_x) / 2)
    else:
        x_extrimum = -b1/(2*a1)
        distance = middle_x_coordinate - x_extrimum

    # positive distance means we need to move right, negative means to move left.
    return distance


def camera_thread(cc):
    global g_frame

    try:
        # TODO: Fix this after updating camera flow.
        cc.prepare_camera()
        cc.start()

        while True:
            # Get next frame synchronously. 
            with lock:
                g_frame = cc.get_single_frame()
                if g_frame is None:
                    continue
                g_frame = cv2.cvtColor(g_frame, cv2.COLOR_BGR2GRAY)

                # Rotate image by 45 deg.
                #g_frame = rotate(g_frame, angle=45, reshape=True)

                # Show the image on screen.
                cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
                cv2.imshow('Current frame', g_frame)

            # Pressing 'q' will terminate the window, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)

    finally:
        cv2.destroyAllWindows()
        cc.shutdown()


# Continously calculate required engine adjustment.
def algorithm_thread(ec, gr):
    global g_frame
    global g_step_size
    global g_should_adjust
    global g_max_val_coord_X
    global g_min_distance_fix
    global g_max_distance_fix

    global g_dist_not_saved
    global g_distances

    prev_step = 0
    try:
        while True:
            with lock:
                if g_frame is None:
                    time.sleep(0.1)
                    continue

                # Adjust the engine accordingly.
                distance = get_distance_to_adjust(g_frame, should_find_min=False)
                if g_should_adjust:
                    #print((g_max_val_coord_X,))
                    #gr.update(np.arange(len(g_max_val_coord_X)), g_max_val_coord_X)
                    
                    # TODO: Improve implementation of translation from pixels to nm.
                    abs_distance = np.abs(distance)
                    if abs_distance > g_min_distance_fix and abs_distance < g_max_distance_fix:
                        # Normalize the distance to move between -150 to 150 nm.
                        sign_distance = distance / abs_distance

                        norm_distance = ((abs_distance - g_min_distance_fix) / (g_max_distance_fix - g_min_distance_fix)) * 150
                        final_distance = norm_distance * sign_distance * (10**-6)

                        # TODO: Maybe the engine is correcting the wrong way.
                        final_distance *= -1
                        
                        if prev_step != g_step_size:
                            print(f"g_step_size: ", g_step_size)
                        prev_step = g_step_size
                        final_distance *= g_step_size

                        # NOTE: This is Tal's suggested method, which didn't quite work for us.
                        # (distance*lamda)/(4*D) = 1.055
                        #final_distance = distance * 1.055 * (10**-6)

                        if len(g_distances) < 1000:
                            g_distances = np.append(g_distances, distance)
                        elif g_dist_not_saved:
                            np.savetxt("distances.txt", g_distances, delimiter=",", fmt="%.6f")
                            g_dist_not_saved = False
                        ec.move_engine(distance=final_distance)

            time.sleep(0.1)
    except Exception as e:
        print(f"Hopefully this was keyboard interrupt: ", e)

    finally:
        # Close engine.
        print("CLOSING ENGINE")
        ec.close()
        #gr.end_update()


def pause_resume_engine():
    global g_should_adjust

    with lock:
        g_should_adjust = not g_should_adjust

def set_min_distance():
    global g_min_distance_fix

    try:
        val = float(input("Enter new min distance to fix: "))
    except ValueError as e:
        print(f"Invalid value received, {e}")
        return

    with lock:
        g_min_distance_fix = val

def set_engine_acc(ec):
    try:
        val = float(input("Enter new value for engine acceleration: "))
    except ValueError as e:
        print(f"Invalid value received, {e}")
        return

    with lock:
        ec.set_velocity(val)

def set_engine_vel(ec):
    try:
        val = float(input("Enter new value for engine velocity: "))
    except ValueError as e:
        print(f"Invalid value received, {e}")
        return

    with lock:
        ec.set_acceleration(val)

def set_step_size():
    global g_step_size

    try:
        val = float(input("Enter new step size: "))
    except ValueError as e:
        print(f"Invalid value received, {e}")
        return

    with lock:
        g_step_size = val

def debug_thread(cc, ec):
    global g_frame
    global g_should_adjust

    while True:
        try:
            cmd = str(input("Enter next command: "))
            cmd = cmd[0]
            if cmd == "s":
                print("Setting minimum distance for correction")
                set_min_distance()
            elif cmd == "a":
                print("Setting engine acceleration")
                set_engine_acc(ec)
            elif cmd == "v":
                print("Setting engine velocity")
                set_engine_vel(ec)
            elif cmd == "p":
                print("Pausing/Resuming the stabilizing algorithm")
                pause_resume_engine()
            elif cmd == "t":
                print("Setting correction step size")
                set_step_size()

        except Exception as e:
            print("Some error..")


def main():
    global g_max_val_coord_X

    lamda = 633 # nm
    D = 150 # pixels

    # Connect to camera.
    #cc = None
    cc = CameraController()
    if not cc.is_opened():
        print("Failed opening camera")
        exit()

    # Connect to engine.
    ec = None
    try:
        pass
        ec = EngineController()
        ec.connect()
        print("Open channel")
        ec.open_channel(1)
        time.sleep(15)
        print("Moving engine")
        ec.move_engine()

        print("Before setting")
        ec.get_movement_data()
        ec.set_velocity(10**-2)
        ec.set_acceleration(10**-2)

        print("After setting")
        ec.get_movement_data()

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

    graph = None
    # graph = gr()
    # frames = np.arange(len(g_max_val_coord_X))
    # graph.prepare(frames, g_max_val_coord_X)

    # Camera is being run in the second thread, we are the algorithm thread.
    algorithm_thread(ec, graph)


if __name__ == '__main__':
    main()
