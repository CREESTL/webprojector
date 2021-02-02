import numpy as np
import cv2


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
        # previous y coordinate
        # it's used to change direction of movement on the second screen
        self.prev_y = None
        # number of a previous screen (from which we move to another one)
        self.prev_screen = None
        # number of a current screen we work with
        self.cur_screen = None
        # temporary variable for previous screen
        self.temp_screen = None
        # if we move from screen 0 to screen 2 - we need to increase X along with Y
        # else - we need to decrease X while Y is increasing (can be -1, 0, 1)
        self.increase_x = 0

    # function clears all screens
    def clear_screens(self):
        del self.screens
        self.screens = [Screen().surface for i in range(3)]

    # FIXME decrease x! now it's not changing

    # function calculates the number of a screen to work with
    # takes x and y
    # returns number of screen and x', y' on that screen
    def scuboscreen(self, x, y):
        print(f'prev_screen = {self.prev_screen}')
        print(f'temp screen is {self.temp_screen}')
        if x < 240:
            if y < 240:
                print("A")
                # zero screen
                # origin at lower right corner
                # y - upwards, x - to the left
                self.cur_screen = 0
                if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                    self.prev_screen = self.temp_screen
                self.temp_screen = 0
                self.prev_y = y
                return self.cur_screen, x, y
            # FIXME bug here!
            elif y >= 240:
                print("B")
                # second screen
                # origin at lower left corner
                # x - to the right, y - upwards
                self.cur_screen = 2
                if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                    self.prev_screen = self.temp_screen
                self.temp_screen = 2
                # moving from screen 1 to screen 2
                if self.prev_screen == 1:
                    if (self.prev_y is not None) and (y > self.prev_y):
                        # moving down the screen
                        # decreasing X as well
                        self.increase_x = -1
                        screen = self.screens[self.cur_screen]
                        screen_height = screen.shape[1]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(x), int(screen_height - (y - 240))
                    elif (self.prev_y is not None) and (y <= self.prev_y):
                        # moving to the right
                        # not doing anything to x
                        self.increase_x = 0
                        screen = self.screens[self.cur_screen]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(x), int(y - 240)

                # moving from screen 0 to screen 2
                if self.prev_screen == 0:
                    if (self.prev_y is not None) and (y > self.prev_y):
                        # moving down the screen
                        self.cur_screen = 2
                        if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                            self.prev_screen = self.temp_screen
                        self.temp_screen = 2
                        # increasing x
                        self.increase_x = 1
                        screen = self.screens[self.cur_screen]
                        screen_height = screen.shape[1]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(screen_height - (y - 240)), int(screen_width - (x - 240))
                    elif (self.prev_y is not None) and (y <= self.prev_y):
                        # moving to the right
                        self.cur_screen = 2
                        if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                            self.prev_screen = self.temp_screen
                        self.temp_screen = 2
                        # npt doing anything to x
                        self.increase_x = 0
                        screen = self.screens[self.cur_screen]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(x - 240), int(screen_width - (y - 240))
        elif x >= 240:
            if y < 240:
                print("C")
                # first screen
                # origin at top right corner
                # y - to the left, x - to us
                self.cur_screen = 1
                if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                    self.prev_screen = self.temp_screen
                self.temp_screen = 1
                screen = self.screens[self.cur_screen]
                screen_height = screen.shape[1]
                self.prev_y = y
                return self.cur_screen, int(y), int(screen_height - (x - 240)),
            elif y >= 240:
                print("D")
                # second screen
                # origin at lower left corner
                # x - to the right, y - upwards
                self.cur_screen = 2
                if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                    self.prev_screen = self.temp_screen
                self.temp_screen = 2
                # moving from screen 1 to screen 2
                if self.prev_screen == 1:
                    if (self.prev_y is not None) and (y > self.prev_y):
                        # moving down the screen
                        # decreasing X as well
                        self.increase_x = -1
                        screen = self.screens[self.cur_screen]
                        screen_height = screen.shape[1]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(screen_width - (x - 240)), int(screen_height - (y - 240)),
                    elif (self.prev_y is not None) and (y <= self.prev_y):
                        # moving to the right
                        # not doing anything to x
                        self.increase_x = 0
                        screen = self.screens[self.cur_screen]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(x - 240), int(screen_width - (y - 240))

                # moving from screen 0 to screen 2
                if self.prev_screen == 0:
                    if (self.prev_y is not None) and (y > self.prev_y):
                        # moving down the screen
                        self.cur_screen = 2
                        if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                            self.prev_screen = self.temp_screen
                        self.temp_screen = 2
                        # increasing x
                        self.increase_x = 1
                        screen = self.screens[self.cur_screen]
                        screen_height = screen.shape[1]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(screen_height - (y - 240)), int(screen_width - (x - 240))
                    elif (self.prev_y is not None) and (y <= self.prev_y):
                        # moving to the right
                        self.cur_screen = 2
                        if (self.temp_screen is not None) and (self.cur_screen != self.temp_screen):
                            self.prev_screen = self.temp_screen
                        self.temp_screen = 2
                        # npt doing anything to x
                        self.increase_x = 0
                        screen = self.screens[self.cur_screen]
                        screen_width = screen.shape[0]
                        self.prev_y = y
                        return self.cur_screen, int(x - 240), int(screen_width - (y - 240))

        # if none of the cases work - return not changed variables
        return self.cur_screen, x, y


    # function draws a circle using module coordinates system
    def draw_point(self, x, y):
        color = (255, 255, 0)
        r = 10
        thickness = 8
        # the screen to draw on and the coordinates on it
        screen_number, x, y = self.scuboscreen(x, y)
        # if number of screen has been calculated correctly
        print(f'cur_screen is {screen_number}')
        if screen_number is not None:
            screen = self.screens[screen_number]
            cv2.circle(screen, (int(y), int(x)), r, color, thickness)
            return self.screens
        else:
            return []



