from pipython import GCSDevice

class engine_controller:
    def __init__(self, pixel_coordinates):
        self.pidevice = None
        self.new_pixel_coordinates = pixel_coordinates
        self.old_coordinates = [0,0]
        self.eng_coordinates = None
        self.relative_moving = None
        pass

    def connect(self):
        self.pidevice = GCSDevice('E-873')
        self.pidevice.InterfaceSetupDlg()
        print(self.pidevice.qIDN())
        
    
    
    def engine_coordinates(self):
        self.eng_coordinates = self.pidevice.qPOS('AXIS_1','AXIS_2')
        print(self.eng_coordinates)


    def mov_rel(self):
        self.relative_moving = self.new_pixel_coordinates - self.old_coordinates
        self.old_coordinates = self.new_pixel_coordinates
        return self.relative_moving


    def move_engine(self):
        self.eng_coordinates = self.eng_coordinates + self.relative_moving
        self.pidevice.MOV({'AXIS_1': self.eng_coordinates[0], 'AXIS_2': self.eng_coordinates[1]})        

    def close(self):
        self.pidevice.CloseConnection()
        