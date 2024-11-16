while True:
    try:
        cmd = str(input("Enter next command: "))
        cmd = cmd[0]
        if cmd == "s":
            print("Setting minimum distance for correction")
            #set_min_distance()
        elif cmd == "a":
            print("Setting engine acceleration")
            #set_engine_acc(ec)
        elif cmd == "v":
            print("Setting engine velocity")
            #set_engine_vel(ec)
        elif cmd == "p":
            print("Pausing/Resuming the stabilizing algorithm")
            #pause_resume_engine()

    except Exception as e:
        print("Some error..")