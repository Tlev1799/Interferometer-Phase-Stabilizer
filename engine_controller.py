from pipython import GCSDevice

class EngineController:
    def __init__(self):
        self.pidevice = None

    def connect(self):
        print("Start connect")
        self.pidevice = GCSDevice('E-873')
        self.pidevice.InterfaceSetupDlg()
        print("qIDN is: {}".format(self.pidevice.qIDN()))

    def open_channel(self, axis):
        self.pidevice.SVO(axis, 1)
        self.pidevice.FRF()
        print("Finished FRF?")
        
    def close_channel(self, axis):
        self.pidevice.SVO(axis, 0)

    def move_engine(self, distance=0, axis=1):
        #import ipdb; ipdb.set_trace()
        self.pidevice.MOV(axis, self.pidevice.qPOS(axis)[axis] + distance)

    def get_movement_data(self):
        acc = self.pidevice.qACC()
        vel = self.pidevice.qVEL()
        pos = self.pidevice.qPOS()

        print(f"Current position: {pos}")
        print(f"Current velocity: {vel}")
        print(f"Current acceleration: {acc}")

    def set_velocity(self, new_vel, axis=1):
        self.pidevice.VEL(axis, new_vel)
        
    def set_acceleration(self, new_acc, axis=1):
        self.pidevice.ACC(axis, new_acc)

    def close(self):
        self.pidevice.CloseConnection()  
