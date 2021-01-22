import json


"""
This version of projector is UNFINISHED
LOTS OF BUGS!
"""


# Single little screen
class Screen:

    def __init__(self, *screen_data):
        if len(screen_data) == 2:
            self.top = screen_data[0]
            self.left = screen_data[1]
        else:
            self.top = []
            self.left = []


# Single module of 3 screens
class Module(Screen):

    def __init__(self, *module_data):
        super().__init__()
        if len(module_data) == 3:
            self.screens = module_data[0]
            self.accel = module_data[1]
            self.gyro = module_data[2]
        else:
            self.accel = ()
            self.gyro = ()
            self.screens = []


# Whole cube of 8 modules
class WOWCube(Module):

    def __init__(self):
        super().__init__()
        self.modules = [Module() for i in range(8)]

    # function creates a cube with default settings
    def load_DEFAULT(self):
        default_data = '''{
        "modules":[
        {"screens":[
        {"top":[3,0],"left":[1,0]},{"top":[1,2],"left":[5,2]},{"top":[5,1],"left":[3,1]}],
        "accel":["-0.00","9.81","-0.00"],
        "gyro":["0.00","0.00","0.00"]
        },
        
        {"screens":[
        {"top":[0,0],"left":[2,0]},{"top":[2,2],"left":[4,2]},{"top":[4,1],"left":[0,1]}],
        "accel":["-0.00","0.00","-9.81"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[1,0],"left":[3,0]},{"top":[3,2],"left":[7,2]},{"top":[7,1],"left":[1,1]}],
        "accel":["-0.00","-9.81","-0.00"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[2,0],"left":[0,0]},{"top":[0,2],"left":[6,2]},{"top":[6,1],"left":[2,1]}],
        "accel":["-0.00","0.00","9.81"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[7,0],"left":[5,0]},{"top":[5,2],"left":[1,2]},{"top":[1,1],"left":[7,1]}],
        "accel":["-0.00","9.81","-0.00"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[4,0],"left":[6,0]},{"top":[6,2],"left":[0,2]},{"top":[0,1],"left":[4,1]}],
        "accel":["-0.00","0.00","-9.81"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[5,0],"left":[7,0]},{"top":[7,2],"left":[3,2]},{"top":[3,1],"left":[5,1]}],
        "accel":["-0.00","-9.81","-0.00"],
        "gyro":["0.00","0.00","0.00"]},
        
        {"screens":[
        {"top":[6,0],"left":[4,0]},{"top":[4,2],"left":[2,2]},{"top":[2,1],"left":[6,1]}],
        "accel":["-0.00","-0.00","9.81"],
        "gyro":["0.00","0.00","0.00"]}
        ]
        }'''
        DEFAULT = self.from_json(default_data)
        return DEFAULT

    # Function creates default settings for the cube
    def _repair(self):
        # Fix accel and gyro in each Module
        for mid in range(len(self.modules)):
            self.modules[mid].accel = tuple(map(float, self.modules[mid].accel))
            self.modules[mid].gyro = tuple(map(float, self.modules[mid].gyro))
        # Assign mid to each Module
        for mid in range(len(self.modules)):
            self.modules[mid].mid = mid
        # Assign sid and parent for each Screen
        for mid in range(len(self.modules)):
            for sid in range(len(self.modules[mid].screens)):
                self.modules[mid].screens[sid].sid = sid
                self.modules[mid].screens[sid].module = self.modules[mid]
        # Assign references for each Screen
        for mid in range(len(self.modules)):
            for sid in range(len(self.modules[mid].screens)):
                self.modules[mid].screens[sid].top = self.modules[self.modules[mid].screens[sid].top[0]].screens[
                    self.modules[mid].screens[sid].top[1]]
                self.modules[mid].screens[sid].left = self.modules[self.modules[mid].screens[sid].left[0]].screens[
                    self.modules[mid].screens[sid].left[1]]
        return self

    # Decodes json data in different ways (one for each part of cube)
    """
    At every level of the json tree walk, the object_hook mechanism expects you to return a dictionary, 
    so if you want to change the subdictionaries into class instances, you have to replace the current 
    object_hook function invocation's input dictionary values with objects, and not just return the object instances.
    """
    def json_hook(self, data_part):
        # data parts form a TREE not a LIST
        # loading one of screens
        # TODO: does it male sense to load Screens and Module if we can just load the whole Cube via last "else" statement???
        if 'top' in data_part:
            data_part['top'] = Screen(data_part)
            return data_part
        # loading module of several screens
        if 'screens' in data_part:
            data_part['screens'] = Module(data_part)
            return data_part
        else:
            # {'modules': [{'screens': <wowcube.projector.Module object....
            # loading the whole cube object
            print("repairing")
            return self._repair()

    # Loads cube from JSON file
    def from_json(self, data):
        return json.loads(data, object_hook=self.json_hook)





