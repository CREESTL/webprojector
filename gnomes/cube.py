import numpy as np
import cv2
from collections import deque

'''

Main file with all functions of the cube

'''


# class represents a single screen
class Screen:
    def __init__(self, num):
        # all objects are projected on its surface
        self.surface = np.zeros((240, 240, 3), np.uint8)
        # the number of a screen on the module
        self.num = num


# class represents a single module
class Module:
    def __init__(self, num):
        # a number of module (max 8)
        self.num = num
        # three screens of a module
        self.screens = [Screen(i).surface for i in range(3)]
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
        self.screens = [Screen(i).surface for i in range(3)]

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
        self.num_sides = 6
        self.trbl = self.update_trbl(request)
        self.grid = self.update_grid()
        self.modules = [Module(i) for i in range(self.num_modules)]

    # function forms a table of relative positions of module
    @staticmethod
    def update_trbl(request):
        # first of all, all information from request we put into list of json strings
        json = []
        for i in range(8):
            json.append(request.json['modules'][i])
        # this is a table of relative screens positions
        # it has such format:
        # {num_module: {num_screen: [[module_counter-clockwise, screen_counter-clockwise], [module_clockwise, screen_clockwise]]...}
        # so it basically shows which screen of which module is located clockwise and counter-clockwise relative to the given screen of the given module
        trbl = {}
        # information about relative position of screens and modules from json into dictionary
        for i, module in enumerate(json):
            trbl[i] = {}
            for j, screen in enumerate(module['screens']):
                trbl[i][j] = [[screen["top"][0], screen["top"][1]], [screen["left"][0], screen["left"][1]]]
        return trbl

    # function gets the number of start module and start screen and forms a list of 4 modules and their screens
    # located on the same side of the cube
    def form_side(self, module_num, screen_num):
        i = 0
        side = []
        while i < 4:
            # adding current module to list
            side.append([module_num, screen_num])
            try:
                # extracting module and it's screen clockwise to current module
                module_clockwise = self.trbl[module_num][screen_num][1][0]
                screen_clockwise = self.trbl[module_num][screen_num][1][1]
                # switching to the new module
                module_num = module_clockwise
                screen_num = screen_clockwise
                i += 1
            except KeyError:
                pass
        return side


    # function returns the screen on the right side of the current module
    # it "looks" around the right corner
    # increasing by 1 ONLY works for up right corner
    def right_screen(self, screen):
        if screen == 0:
            return 1
        elif screen == 1:
            return 2
        elif screen == 2:
            return 0

    # function returns the screen upwards from the current module screen
    # it "looks" around the up corner
    # works ONLY for up right corner
    def up_screen(self, screen):
        if screen == 0:
            return 2
        elif screen == 1:
            return 0
        elif screen == 2:
            return 1

    # function returns the screen downwards from tje current module screen
    # it "looks" around the down corner
    # works ONLY for lower left corner
    def down_screen(self, screen):
        if screen == 0:
            return 2
        elif screen == 1:
            return 0
        elif screen == 2:
            return 1


    # front - 0; up - 1; left - 2; right - 3; back - 4; down - 5;
    def update_grid(self):
        grid = {}

        # FRONT SIDE
        grid[0] = self.form_side(0, 0)

        # DOWN SIDE
        # take the lower left module of the front side and process it
        # it will form down side
        new_module = grid[0][3][0]
        new_screen = self.down_screen(grid[0][3][1])
        grid[5] = self.form_side(new_module, new_screen)

        # RIGHT SIDE
        # take the upper right module of front side and process it
        # it will form right side
        new_module = grid[0][1][0]
        new_screen = self.right_screen(grid[0][1][1])
        grid[3] = self.form_side(new_module, new_screen)

        # BACK SIDE
        # take the upper right module of the right side and process it
        # it will form back side
        new_module = grid[3][1][0]
        new_screen = self.right_screen(grid[3][1][1])
        grid[4] = self.form_side(new_module, new_screen)

        # LEFT SIDE
        # take the upper right module of the back side and process it
        # it will form right side
        new_module = grid[4][1][0]
        new_screen = self.right_screen(grid[4][1][1])
        grid[2] = self.form_side(new_module, new_screen)

        # UP SIDE
        # take the upper right module of the back side and process it
        # it will form up side
        new_module = grid[4][1][0]
        new_screen = self.up_screen(grid[4][1][1])
        grid[1] = self.form_side(new_module, new_screen)

        sorted_grid = {}
        sorted_keys = sorted(grid)
        for sk in sorted_keys:
            sorted_grid[sk] = grid[sk]
        grid = sorted_grid
        print(f'\nGRID: ')
        for side, info in grid.items():
            print(side, info)
        return grid


    # function returns position of module in grid
    def find_in_grid(self, module, screen):
        for side, info in self.grid.items():
            pair = [module, screen]
            if pair in info:
                return side, info.index(pair)


    # function calculates position of an object located on another module relative to current module origin
    # initial module - the module where the object is currently located
    # x, y - scubic coordinates of the object on the module
    # compared_module - the module which scubic coordinates system we use to recalculate coordinates (x, y)
    # returns x', y' of the compared_module coordinates system
    def recalc_pos(self, initial_module, x, y, compared_module):
        # we DONT need to move object anywhere
        # we ONLY need the coords of origin
        #module = self.modules[initial_module]
        # module.move(x, y)
        # initial_module_screen = module.get_cur_screen()
        initial_module_side, initial_module_index = self.find_in_grid(initial_module, 0)
        # we have to look for compared module 0 screen (it's origin)
        compared_module_side, compared_module_index = self.find_in_grid(compared_module, 0)
        print(f'initial module origin: side {initial_module_side} index {initial_module_index}')
        print(f'compared module origin: side {compared_module_side} index {compared_module_index}')
        # for (0, 120, 120, 1) should return (-120, -120)
        # for (0, 120, 60, 2) should return (-120, -60)
        # for (0, 360, 120, 1) should return (-360, -120)
        # for (0, 60, 400, 5) should return (560, 60)
        # for (0, 120, 120, 7) should return (-840, -120)

        # TODO only process 0 screens of both modules
        # TODO that is: if we have module 0 and coords on it are 360, 120 then the object would be
        # TODO on right side, but we have to calculate new coords relative to the initial module 0 ORIGIN!

        rotate_times = abs(compared_module_index - initial_module_index)
        # front - 0; up - 1; left - 2; right - 3; back - 4; down - 5;
        print(f'rotate time is {rotate_times}')


        grid_graph = {}
        #                up, left, right, down
        grid_graph[0] = [1, 2, 3, 5]
        grid_graph[1] = [4, 1, 3, 0]
        grid_graph[2] = [1, 4, 0, 5]
        grid_graph[3] = [1, 0, 4, 5]
        grid_graph[4] = [1, 3, 2, 5]
        grid_graph[5] = [0, 2, 3, 4]

        # changes of X and Y depending on direction
        dx, dy = 0, 0


        # the easiest option - if compared module and initial module are the same module
        if compared_module == initial_module:
            return x, y

        # if compared module is located on the same side as the initial one
        if compared_module_side == initial_module_side:
            for i in range(rotate_times):
                x, y = -y, x
            return x, y

        # TODO test each side if initial_index == compared_index

        # TODO test this:
        # FIXME current version only works if initial module is 0, so if the module with another number is input
        # FIXME then we have to rotate it anticlockwise to "become" module 0
        # FIXME then we "teleport" it to module zero of the opposite side and do the other magick stuff
        prepare_rotate_times = initial_module_index - 0
        for i in range(prepare_rotate_times):
            x, y = -y, x
        print(f"initial coords relative to module 0 of initial side are ({x},{y})")

        # if compared module is located on one of four neighbour sides
        if compared_module_side in grid_graph[initial_module_side]:
            print('compared module`s origin is on the neighbour side')
            direction = grid_graph[initial_module_side].index(compared_module_side)
            print(f'direction is {direction}')
            # up
            if direction == 0:
                # imagine that we moved current module to the neighbour side (up in this case)
                # so (0, 0) becomes (1, 0)
                dy = 480
                dx = 0
                for i in range(rotate_times):
                    x, y = y, -x
                # x is the same
            # left
            elif direction == 1:
                dy = 0
                dx = 480
                for i in range(rotate_times):
                    x, y = y, -x
            # right
            elif direction == 2:
                dy = 0
                dx = -480
                for i in range(rotate_times):
                    x, y = y, -x
            # down
            elif direction == 3:
                dy = -480
                dx = 0
                for i in range(rotate_times):
                    x, y = y, -x

        else:
            print("BACK")
            # in this case compared module is on the opposite side
            # moving to upper left module of back side
            # in this case we have to do it here - not in the end of function
            x = -(960 - x)
            # we don't change y here

            print(f'x and y relative to 0 module of opposite side are {x}, {y}')

            for i in range(rotate_times):
                # it's weird, but on the 0 module of the opposite side the object has coordinates that look nothing like
                # coordinates on the other three modules of the same side
                # so with first rotation coordinates have to be transformed like that
                if i == 0:
                    x, y = 960 - y, 960 + x
                else:
                    x, y = y, -x
        x += dx
        y += dy
        return x, y




