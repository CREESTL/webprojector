import numpy as np
import cv2
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
        self.screens = [Screen(i) for i in range(3)]
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
        self.screens = [Screen(i) for i in range(3)]

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
    # it just changes X and Y
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
            # FIXME bug here? are screens actually changed?
            cv2.circle(screen.surface, (int(x), int(y)), r, color, thickness)
            for img_num, screen in enumerate(self.screens):
                # FIXME doesn't seem like that: here all screens are black after saving into directory
                cv2.imwrite(
                    '/home/creestl/programming/python_coding/wowcube/webprojector/gnomes/debug/screens/%i.jpg' % img_num,
                    screen.surface)
            return self.screens
        else:
            return []


# class represents the whole cube of 8 modules and 24 screens
class Cube:
    def __init__(self):
        self.num_screens = 24
        self.num_modules = 8
        self.num_sides = 6
        self.trbl = None
        self.grid = None
        self.modules = [Module(i) for i in range(self.num_modules)]

    # function forms a table of relative positions of module
    def update_trbl(self, request):
        # first of all, all information from request we put into list of json strings
        json = []
        if request.json['modules']:
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
            self.trbl = trbl

    # function gets the number of start module and start screen and forms a list of 4 modules and their screens
    # located on the same side of the cube
    def form_side(self, module_num, screen_num):
        i = 0
        side = []
        while i < 4:
            # this can happen when trbl.update was called when the cube was still in rotation
            if (module_num == -1) or (screen_num == -1):
                # return no side
                return None
            else:
                # adding current module to list
                side.append([module_num, screen_num])
                # extracting module and it's screen clockwise to current module
                module_clockwise = self.trbl[module_num][screen_num][1][0]
                screen_clockwise = self.trbl[module_num][screen_num][1][1]
                # switching to the new module
                module_num = module_clockwise
                screen_num = screen_clockwise
                i += 1
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

    # it has such format:
    # {side_num: [[first_module_num, it's screen_num], [second_module_num, it's screen_num], [third_module_num, it's screen_num].....}
    # front - 0; up - 1; left - 2; right - 3; back - 4; down - 5;
    def update_grid(self, request):

        # before updating the grid we have to update the trbl
        self.update_trbl(request)

        grid = {}

        # FRONT SIDE
        grid[0] = self.form_side(0, 0)
        # it can happen if the cube is still in rotation and we cannot form the side
        if grid[0] is None:
            return

        # DOWN SIDE
        # take the lower left module of the front side and process it
        # it will form down side
        new_module = grid[0][3][0]
        new_screen = self.down_screen(grid[0][3][1])
        grid[5] = self.form_side(new_module, new_screen)
        if grid[5] is None:
            return

        # RIGHT SIDE
        # take the upper right module of front side and process it
        # it will form right side
        new_module = grid[0][1][0]
        new_screen = self.right_screen(grid[0][1][1])
        grid[3] = self.form_side(new_module, new_screen)
        if grid[3] is None:
            return

        # BACK SIDE
        # take the upper right module of the right side and process it
        # it will form back side
        new_module = grid[3][1][0]
        new_screen = self.right_screen(grid[3][1][1])
        grid[4] = self.form_side(new_module, new_screen)
        if grid[3] is None:
            return

        # LEFT SIDE
        # take the upper right module of the back side and process it
        # it will form right side
        new_module = grid[4][1][0]
        new_screen = self.right_screen(grid[4][1][1])
        grid[2] = self.form_side(new_module, new_screen)
        if grid[2] is None:
            return

        # UP SIDE
        # take the upper right module of the back side and process it
        # it will form up side
        new_module = grid[4][1][0]
        new_screen = self.up_screen(grid[4][1][1])
        grid[1] = self.form_side(new_module, new_screen)
        if grid[1] is None:
            return

        sorted_grid = {}
        sorted_keys = sorted(grid)
        for sk in sorted_keys:
            sorted_grid[sk] = grid[sk]
        grid = sorted_grid

        self.grid = grid

    # function returns position of module in grid
    def find_in_grid(self, module, screen):
        for side, info in self.grid.items():
            pair = [module, screen]
            if pair in info:
                # returns number of side and index of the module on the side
                return side, info.index(pair)

    # function calculates on which screen of the initial module the object is located
    # further coordinates transformations are based on that screen number
    @ staticmethod
    def find_screen(x, y):
        if (x <= 240) and (y <= 240):
            return 0
        elif (x <= 240) and (y >= 240):
            return 1
        elif (x > 240) and (y <= 240):
            return 2
        elif (x > 240) and (y > 240):
            return 1


    # function calculates position of an object located on another module relative to current module origin
    # initial module - the module where the object is currently located
    # x, y - scubic coordinates of the object on the module
    # compared_module - the module which scubic coordinates system we use to recalculate coordinates (x, y)
    # returns x', y' of the compared_module coordinates system
    def recalc_coords(self, initial_module, x, y, compared_module):
        # if the grid failed to update for some reason then we indicate that new coords were not calculated
        if self.grid is None:
            return None, None
        initial_module_side, initial_module_index = self.find_in_grid(initial_module, 0)
        # we have to look for compared module 0 screen (it's origin)
        compared_module_side, compared_module_index = self.find_in_grid(compared_module, 0)
        #print(f'\ninitial module origin: side {initial_module_side} index {initial_module_index}')
        #print(f'compared module origin: side {compared_module_side} index {compared_module_index}')

        # how many times we have to rotate 0 module of compared side to reach the compared module
        rotate_times = abs(compared_module_index - initial_module_index)
        # front - 0; up - 1; left - 2; right - 3; back - 4; down - 5;
        #            up, left, right, down
        grid_graph = {0: [1, 2, 3, 5], 1: [4, 1, 3, 0], 2: [1, 4, 0, 5], 3: [1, 0, 4, 5], 4: [1, 3, 2, 5],
                      5: [0, 2, 3, 4]}

        # the easiest option - if compared module and initial module are the same module
        if compared_module == initial_module:
            return x, y

        # WORKS FULL
        # front
        # if compared module is located on the same side as the initial one
        if compared_module_side == initial_module_side:
            #print('compared module`s origin is on the same side')
            initial_screen = self.find_screen(x, y)
            if initial_screen == 0:
                for i in range(rotate_times):
                    x, y = y, -x
                return x, y
            elif initial_screen == 1:
                if x <= 240:
                    for i in range(rotate_times):
                        x, y = y, -x
                    return x, y
                elif x > 240:
                    for i in range(rotate_times):
                        if (i > 0) and (x > 0):
                            x = -x
                        y = abs(y) - 480 if i == 0 or i == 1 else -(abs(y) - 480)
                    return x, y
            elif initial_screen == 2:
                for i in range(rotate_times):
                    if (i > 0) and (x > 0):
                        x = -x
                    y = abs(y) - 480 if i == 0 or i == 1 else -(abs(y) - 480)
                return x, y


        # we rotate initial module counter-clockwise to "make" it module 0 of initial side
        prepare_rotate_times = initial_module_index - 0
        for i in range(prepare_rotate_times):
            x, y = y, -x

        # if compared module is located on one of four neighbour sides
        if compared_module_side in grid_graph[initial_module_side]:
            #print('compared module`s origin is on the up, down, left or right side')
            direction = grid_graph[initial_module_side].index(compared_module_side)
            #print(f'direction is {direction}')
            # now depending on direction where the compared module is located we make coordinates transformations
            # I won't explain all calculations here - it's too much

            # WORKS FULL
            # up
            if direction == 0:
                initial_screen = self.find_screen(x, y)
                if initial_screen == 0:
                    y -= 480
                    for i in range(rotate_times):
                        x, y = y, -x
                elif initial_screen == 1:
                    if x <= 240:
                        y -= 480
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                    else:
                        y_copy = y
                        y = -(480 - x)
                        x = 480 - y_copy
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                elif initial_screen == 2:
                    y = - (480 - x)
                    x = 480 - y
                    for i in range(rotate_times):
                        x = -x if x > 0 else x
                        y = abs(y) - 480
            # WORKS FULL
            # left
            elif direction == 1:
                initial_screen = self.find_screen(x, y)
                if initial_screen == 0:
                    x -= 480
                    for i in range(rotate_times):
                        x = -x if i == 0 or i == 2 else x
                        y = 480 - abs(y) if i < 1 else abs(y) - 480
                elif initial_screen == 1:
                    if (x <= 240) and (y >= 240):
                        x_copy = x
                        x = - (480 - y)
                        y = (480 - x_copy)
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                    elif (x > 240) and (y > 240):
                        x = - (480 - x)
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                elif initial_screen == 2:
                    x = - (480 - x)
                    for i in range(rotate_times):
                        x, y = y, -x
                    return x, y

            # WORKS FULL
            # right
            elif direction == 2:
                initial_screen = self.find_screen(x, y)
                if initial_screen == 0:
                    x += 480
                    for i in range(rotate_times):
                        if (i > 0) and (x > 0):
                            x = -x
                        y = abs(y) - 480 if i == 0 or i == 1 else -(abs(y) - 480)
                    return x, y
                elif initial_screen == 1:
                    if x <= 240:
                        x += 480
                        for i in range(rotate_times):
                            if (i > 0) and (x > 0):
                                x = -x
                            y = abs(y) - 480 if i ==0 or i == 1 else -(abs(y) - 480)
                        return x, y
                    elif x > 240:
                        x_copy = x
                        x = 480 + (480 - y)
                        y = x_copy
                        for i in range(rotate_times):
                            if (i > 0) and (x > 0):
                                x = -x
                            y = abs(y) - 480 if i ==0 or i == 1 else -(abs(y) - 480)
                        return x, y
                elif initial_screen == 2:
                    x_copy = x
                    y_copy = y
                    x += 480
                    for i in range(rotate_times):
                        if i == 0:
                            x = 720 + (240 - y_copy)
                            y = -(480 - x_copy)
                            return x, y
                        elif i == 2:
                            x = -(720 + (240 - y_copy))
                            y = 480 - x_copy
                            return x, y
                        else:
                            x = -(480 + x_copy)
                            y = -y_copy
                            return x, y
            # WORKS FULL
            # down
            elif direction == 3:
                initial_screen = self.find_screen(x, y)
                if initial_screen == 0:
                    y += 480
                    for i in range(rotate_times):
                        x, y = y, -x
                    return x, y
                elif initial_screen == 1:
                    if x <= 240:
                        x = 720 + (240 - x)
                        y = 480 - y
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                    if x > 240:
                        x_copy = x
                        x = 720 + (y - 240)
                        y = 480 - x_copy
                        for i in range(rotate_times):
                            x, y = y, -x
                        return x, y
                elif initial_screen == 2:
                    x_copy = x
                    x = 480 + y
                    y = 480 - x_copy
                    for i in range(rotate_times):
                        if (i > 0) and (x > 0):
                            x = -x
                        y = abs(y) - 480 if i == 0 or i == 1 else -(abs(y) - 480)
                    return x, y
        # back
        else:
            #print('compared module`s origin is on the back side')
            initial_screen = self.find_screen(x, y)
            if initial_screen == 0:
                x_copy = x
                y_copy = y
                x = -(960 - x)
                for i in range(rotate_times):
                    if i == 0:
                        x = 960 - y_copy
                        y = x_copy
                    if i == 1:
                        x = 960 - x_copy
                        y = -y_copy
                    if i == 2:
                        x = -(960 - y_copy)
                        y = -x_copy
                return x, y
            elif initial_screen == 1:
                if x <= 240:
                    x_copy = x
                    x = -(960 - y)
                    y = 480 - x_copy
                    for i in range(rotate_times):
                        x = -x if i == 0 or i == 2 else x
                        y = 480 - abs(y) if i < 1 else abs(y) - 480
                    return x, y
                if x > 240:
                    x = -(960 - x)
                    for i in range(rotate_times):
                        x = -x if i == 0 or i == 2 else x
                        y = 480 - abs(y) if i < 1 else abs(y) - 480
                    return x, y
            elif initial_screen == 2:
                x = -(960 - x)
                for i in range(rotate_times):
                    x = -x if i == 0 or i == 2 else x
                    y = 480 - abs(y) if i < 1 else abs(y) - 480
                return x, y
        return x, y

    # function clears all screens of the cube
    def clear_screens(self):
        for module in self.modules:
            module.clear_screens()




