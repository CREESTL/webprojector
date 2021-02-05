import numpy as np
import cv2


'''

Main file with all functions of the cube

'''


# class represents a single screen
class Screen:
    def __init__(self):
        # all objects are projected on its surface
        self.surface = np.zeros((240, 240, 3), np.uint8)


# class represents a single module
class Module:
    def __init__(self, num):
        # a number of module (max 8)
        self.num = num
        # three screens of a module
        self.screens = [Screen().surface for i in range(3)]
        # number of current screen
        self.cur_screen = 0
        # list of two coordinates: x and y
        self.coords = [int, int]
        # in this order screens are to be processed
        self.screens_order = [0, 1, 2]

    # function draws an object using scubic coordinates of the module
    def update_screens(self, x, y):
        self.move(x, y)
        # draw an object on those coordinates
        self.screens = self.draw_point()
        return self.screens

    # function clears all screens
    def clear_screens(self):
        del self.screens
        self.screens = [Screen().surface for i in range(3)]

    # function moves the object using ONE coordinate
    # coord - module of coordinate we move to
    # coord_num - position of the coordinate in self.coords array (0 or 1 for X and same for Y)
    def step(self, coord, coord_num):
        # function calculates screen number using ONE coordinate, so for both X and Y screen number must be 0
        self.cur_screen = 0
        # moving outside the screen
        if coord > 240:
            # making X of new screen equal to Y of previous screen
            self.coords[coord_num] = self.coords[not coord_num]
            # calculating a new Y of the new screen
            self.coords[not coord_num] = 240 - (coord - 240)
            if coord_num == 0:
                # if we changed X then change current screen skipping one (0 -> 2)
                self.cur_screen = (self.cur_screen + 2) % 3
            else:
                # if we changed Y then change current screen without skipping one (0 -> 1)
                self.cur_screen = (self.cur_screen + 1) % 3
            # indicates that we moved to the other screen
            return True
        else:
            # changing coordinates on current screen
            self.coords[coord_num] = coord
            # indicates that we did not move to the other screen
            return False

    # function moves the object to the given TWO coordinates
    def move(self, x, y):
        # if we changed X and moved to the other screen then we change axes places
        if self.step(x, 0):
            self.step(y, 0)
        # if we changed X and stayed on the same screen then we don't change axes places
        else:
            self.step(y, 1)

    # function returns the X coordinate of an object
    def x(self):
        return self.coords[0]

    # function returns the Y coordinate of an object
    def y(self):
        return self.coords[1]

    # function returns the number of current screen of a module
    def get_cur_screen(self):
        return self.screens_order[self.cur_screen]

    # function returns everything for drawing an object on a screen
    def get_attributes(self):
        return self.screens_order[self.cur_screen], self.coords[0], self.coords[1]

    # function draws a circle using module coordinates system
    def draw_point(self):
        color = (255, 255, 0)
        r = 10
        thickness = 8
        # the screen to draw on and the coordinates on it
        screen_number, x, y = self.get_attributes()
        if screen_number is not None:
            screen = self.screens[screen_number]
            cv2.circle(screen, (int(x), int(y)), r, color, thickness)
            return self.screens
        else:
            return []


# class represents the whole cube of 8 modules and 24 screens
class Cube:
    def __init__(self, request):
        self.num_screens = 24
        self.num_modules = 8
        self.trbl = self.update_trbl(request)
        self.modules = [Module(i) for i in range(self.num_screens)]

    # function forms a table of relative positions of module
    @staticmethod
    def update_trbl(request):
        trbl = []
        for i in range(8):
            trbl.append(request.json['modules'][i])
        return trbl

    # function calculates position of an object located on another module relative to current module origin
    def recalc_pos(self):
        # information about relative position of screens and modules
        for i, m in enumerate(self.trbl):
            print(f'MODULE {i}')
            for j, s in enumerate(m['screens']):
                print(f'--screen {j}')
                print(f'----counter clockwise: module {s["top"][0]} screen {s["top"][1]}')
                print(f'----clockwise: module {s["left"][0]} screen {s["left"][1]}')
        print("==========\n")
        pass
