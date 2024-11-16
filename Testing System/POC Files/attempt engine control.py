from pipython import GCSDevice

with GCSDevice('E-873') as controller:
    controller.InterfaceSetupDlg()

    axis = 1

    # Query current position units
    position = controller.qPOS(axis)  # Query position
    print(f"Current position: {position[axis]} units")

    # Query current velocity units
    velocity = controller.qVEL(axis)  # Query velocity
    print(f"Current velocity: {velocity[axis]} units/s")

    # Query current acceleration units
    acceleration = controller.qACC(axis)  # Query acceleration
    print(f"Current acceleration: {acceleration[axis]} units/s²")

    # Set velocity (in device-specific units)
    controller.VEL(axis, 10.0)  # Replace 10.0 with the desired velocity

    # Set acceleration (in device-specific units)
    controller.ACC(axis, 20.0)  # Replace 20.0 with the desired acceleration

    # Move the stage
    controller.MOV(axis, 50.0)  # Replace 50.0 with the desired target position

    # Wait until the movement is complete
    controller.WAIT(axis)
