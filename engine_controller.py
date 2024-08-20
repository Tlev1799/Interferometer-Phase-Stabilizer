from pipython import GCSDevice

class EngineController:
    def __init__(self):
        self.pidevice = None

    def connect(self):
        print("Start connect")
        self.pidevice = GCSDevice('E-873')
        self.pidevice.InterfaczeSetupDlg()
        print("qIDN is: {}".format(self.pidevice.qIDN()))

    def move_engine(self, distance):
        self.pidevice.OSM(1, distance)

    def close(self):
        self.pidevice.CloseConnection()  
