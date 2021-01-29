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

    # function clears all screens
    def clear_screens(self):
        del self.screens
        self.screens = [Screen().surface for i in range(3)]

    # FIXME add function that takes x and y and returns the screen number and the
    # FIXME coordinates on that screen
    # FIXME it should be a part of the function below
    # FIXME it should process screen 2 in a special way and count coordinates in two situations:
    # FIXME when Y is increasing
    # FIXME when Y is decreasing
    # FIXME it has to REMEMBER from which screen we moved to the current screen because
    # FIXME if we move from screen 1 to screen 2 and increase Y then we have to decrease X
    # FIXME but if we move from screen 0 to screen 2 then we shouldn't touch X at all

    # function draws a circle using module coordinates system
    def draw_point(self, x, y):
        color = (255, 255, 0)
        r = 10
        thickness = 8
        if x < 240:
            if y < 240:
                # zero screen
                # origin at lower right corner
                # y - upwards, x - to the left
                screen = self.screens[0]
                cv2.circle(screen, (int(y), int(x)), r, color, thickness)
                self.prev_y = y
                return self.screens
            elif y >= 240:
                # second screen
                # origin at lower left corner
                # x - upwards, y - to the right
                screen = self.screens[2]
                screen_height = screen.shape[1]
                cv2.circle(screen, (int(x), int(screen_height - (y - 240))), r, color, thickness)
                self.prev_y = y
                return self.screens
        elif x >= 240:
            if y < 240:
                # first screen
                # origin at top right corner
                # y - to the left, x - to us
                screen = self.screens[1]
                screen_height = screen.shape[1]
                cv2.circle(screen, (int(screen_height - (x - 240)), int(y)), r, color, thickness)
                self.prev_y = y
                return self.screens
            elif y >= 240:
                # second screen
                # origin at lower left corner
                # x - upwards, y - to the right
                if (self.prev_y is not None) and (y > self.prev_y):
                    # moving down the screen
                    screen = self.screens[2]
                    screen_height = screen.shape[1]
                    screen_width = screen.shape[0]
                    cv2.circle(screen, (int(screen_height - (y - 240)), int(screen_width - (x - 240))), r, color, thickness)
                elif (self.prev_y is not None) and (y <= self.prev_y):
                    # moving to the right
                    screen = self.screens[2]
                    screen_height = screen.shape[1]
                    screen_width = screen.shape[0]
                    cv2.circle(screen, (int(x - 240), int(screen_width - (y - 240))), r, color, thickness)
                self.prev_y = y
                return self.screens
        else:
            return []


