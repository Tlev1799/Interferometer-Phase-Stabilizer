# -*- coding: utf-8 -*-
"""
Stage Controller File
"""
from newportxps import NewportXPS


class StageController:
    def __init__(self, host="10.10.208.8", stage_name='Group2.Pos'):
        self.stage_name = stage_name
    
        self.xps = NewportXPS(host)
        self.xps.get_group_status()
        self.xps.get_stage_position(stage_name)
        self.xps.stages
        
    def move_relative_mm(self, distance):
        self.xps.move_stage(self.stage_name, distance, relative=True)
