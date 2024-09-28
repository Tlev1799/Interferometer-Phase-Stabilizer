from engine_controller import EngineController
from ltc_camera_controller import CameraController
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
g_step_size = 0.2 # Step size of the feedback.
g_should_adjust = True
g_min_distance_fix = 20
g_max_distance_fix = 300
g_max_val_coord_X = np.array([])
g_correction_dist = np.array([])

# Counter for saving frames in files.
saved_frames_counter = 0

def get_distance_to_adjust(frame, should_find_min=False):
    global g_max_val_coord_X
    global g_correction_dist

    # Find min/max and calculate distance (in pixels) from the middle.
    distance = 0
    x, left_of_x, right_of_x = 0, 0, 0
    middle_x_coordinate = (len(frame[0])/2) - 0.5
    # print(f"kdgrkjebkjref: ", len(frame)/2)
    # print(f"Also: ", len(frame[0])/2)
    #print(f"middle coordinate: {middle_x_coordinate}")

    if should_find_min:
        #print("Finding min")
        return_tuple = find_min_x_coordinate(frame)
    else:
        #print("Finding max")
        return_tuple = find_max_x_coordinate(frame)

    x, left_of_x, right_of_x = [int(a) for a in return_tuple]
    #print(f"indexes: {left_of_x}, {x}, {right_of_x}")

    # Debug for later graph drawing. This line assumes we search for max value.
    if len(g_max_val_coord_X) < 1000:
        g_max_val_coord_X = np.append(g_max_val_coord_X, int(x))

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

    #print(f"maximum: {x_extrimum}")
    #print(f"distance: {distance}")

    # TODO: Distance now contains a value in pixels. We still need to convert it to nm for
    # the actual adjustment.

    if len(g_correction_dist) < 1000:
        #print(f"Distance is: ", distance)
        g_correction_dist = np.append(g_correction_dist, int(distance))
        if np.abs(distance) > 1000:
            ipdb.set_trace()

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
                g_frame = cv2.cvtColor(g_frame, cv2.COLOR_BGR2GRAY)

                # minval = np.min(gray_frame)
                # maxval = np.max(gray_frame)

                # min_coords = np.argwhere(gray_frame == minval)[0]
                # max_coords = np.argwhere(gray_frame == maxval)[0]

                #print("Minimum Value:", minval, "at coordinates:", min_coords)
                #print("Maximum Value:", maxval, "at coordinates:", max_coords)

                #time.sleep(5)

                #print("Next g_frame:")
                #print(gray_frame)
                #ipdb.set_trace()
                #time.sleep(10)
                #g_frame = cv2.GaussianBlur(g_frame, (5, 5), 0)

                #g_frame = cv2.medianBlur(g_frame, 3)

                # Convert the image to type that cv2 supports.
                #frame_uint8 = cv2.convertScaleAbs(g_frame, alpha=(255.0/65535.0))
                #normalized_frame = cv2.normalize(g_frame, None, 0, 255, cv2.NORM_MINMAX)
                #g_frame = cv2.transpose(g_frame)
                #frame_uint8 = (g_frame / 1023.0)*255
                

            # Note: Here we no longer use g_frame so we release the lock,
            #       holding it unecessarily will just slow us down.

            # Show the image on screen.
            cv2.namedWindow('Current frame', cv2.WINDOW_NORMAL)
            #cv2.imshow('Current frame', frame_uint8)
            cv2.imshow('Current frame', g_frame)


            # Pressing 'q' will terminate the window, otherwise this just polls for 1ms.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)

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
    global g_max_distance_fix

    #index = 0
    debug_counter = 1
    file_name_counter = 0
    prev_step = 0
    try:
        while True:
            # time.sleep(5)
            # continue
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
                    # with open(f"debug\\debug_text{file_name_counter}.txt", "a") as f:
                    #     f.write(f"frame: {frame}\n\nFound max at: {((len(frame)/2) - 0.5) - distance}\nDistance to middle: {distance}\n\n\n")
                    # debug_counter += 1
                    # if 0 == debug_counter % 100:
                    #     debug_counter = 1
                    #     file_name_counter += 1
                    
                    #print(f"Distance calculated {distance}")
                    
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

                        # (distance*lamda)/(4*D) = 1.055
                        #final_distance = distance * 1.055 * (10**-6)

                        ec.move_engine(distance=final_distance)

            # Wait for 100ms to let g_frame time to update in the other thread.
            time.sleep(0.1)
    except Exception as e:
        print(f"Hopefully this was keyboard interrupt: ", e)

    finally:
        # Save vectors to file.
        np.savetxt("max_val_arr.txt", g_max_val_coord_X, delimiter=",", fmt="%d")
        np.savetxt("correction_dist_arr.txt", g_correction_dist, delimiter=",", fmt="%d")

        # Close engine.
        print("CLOSING ENGINE")
        ec.close()

# def set_feedback_step_size():
#     try:
#         new_k = float(input("Enter new value for size step"))

#         if new_k <= 0 or new_k >= 1:
#             print("ERROR: K must satisfy: 0 < k < 1")
#             return
        
#         # Update k synchorniously
#         with lock:
#             g_step_size = new_k

#     except ValueError:
#         print("Invalid value for k")


def manual_adjust(cc, ec):

    # Stop capturing and adjusting using the lock on g_frame
    with lock:
        while True:
            try:
                # Manually adjsut distance.
                distance = float(input("Enter distance to adjust: "))
                ec.move_engine(distance=distance)

                # Display updated frame for 1 second.
                time.sleep(0.1)
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
            #cc.cam.set_exposure(exposure_time)
            #print(f"Successfully set exposure time to: {exposure_time}")
            print("Not supported for ltc camera!")
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
        value = float(input("Enter engine position: "))
        ec.move_engine(distance=value)
    except:
        print("ERROR")
        return


def set_engine_data(ec):
    try:
        value = float(input("Value for acceleration: "))
        if 0 != value:
            ec.set_acceleration(value)

        value = float(input("Value for velocity: "))
        if 0 != value:
            ec.set_velocity(value)
    except:
        print("Error")
        return


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
    
    # Declare globals to be used.
    global g_frame
    #global g_step_size
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

    # For manually adjusting engine.
    #keyboard.add_hotkey('a', manual_adjust, args=(cc, ec))

    # Change step size (value of k)
    # keyboard.add_hotkey('k', set_feedback_step_size)

    # # Display calculated distance to adjust for the current frame.
    # keyboard.add_hotkey('d', display_distance)

    # # Set exposure time.
    # keyboard.add_hotkey('x', set_exposure_time, args=(cc, ))

    # # Pause/resume adjusting algorithm.
    # keyboard.add_hotkey('p', pause_resume_engine)

    # # Set break point (Blocks camera footage !)
    # keyboard.add_hotkey('b', pdb, args=(cc, ec))

    # #keyboard.add_hotkey('s', save_frame_in_file)

    # keyboard.add_hotkey('z', control_engine, args=(ec, ))

    # keyboard.add_hotkey('s', set_engine_data, args=(ec, ))

    # keyboard.add_hotkey('m', set_min_distance)

    # # Wait forever for different keys. 'e' will exit the debug thread. 
    # keyboard.wait('e')

def main():

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
        #import ipdb; ipdb.set_trace()
        print("Open channel")
        ec.open_channel(1)
        time.sleep(15)
        print("Moving engine")
        ec.move_engine()

        print("Before setting")
        ec.get_movement_data()
        ec.set_velocity(10**-3)
        ec.set_acceleration(10**-3)

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
    # dbg_thread = threading.Thread(target=debug_thread, args=(cc, ec), daemon=True)
    # dbg_thread.start()

    # Camera is being run in the second thread, we are the algorithm thread.
    algorithm_thread(ec)


if __name__ == '__main__':
    main()
