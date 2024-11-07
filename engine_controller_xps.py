from newportxps import NewportXPS

class XPSController:
    def __init__(self, ip, username=None, password=None):
        self.xps = None
        self.ip = ip
        self.username = username
        self.passwd = password
        
    def connect(self):
        self.xps = NewportXPS(self.ip, username=self.username, password=self.passwd)
        print(self.xps.status_report())

    def move_engine(self, distance):
        # TODO: What stage name??
        self.xps.move_stage('some_stage_name', distance, relative=True)
