'''

Here should be functions for transforming object coordinates to sphero-cubic coordinates

'''


import numpy as np
import cv2


# class represents a single screen
class Screen:
    def __init__(self):
        # all objects are projected on its surface
        self.surface = np.zeros((240, 240, 3), np.uint8)

    # function gets a clockwise and anticlockwise neighbours of a screen
    def update_neighbours(self, modules):
        return

# class represents a single module
class Module:
    def __init__(self, num):
        # a number of module (max 8)
        self.num = num
        # three screens of a module
        self.screens = [Screen().surface for i in range(3)]

    # function draws a circle using module coordinates system
    def draw_point(self, x, y):
        color = (255, 255, 0)
        r = 10
        thikness = 8
        # zero screen
        # origin at lower right corner
        # y - upwards, x - to the left
        if (x < 240) and (y < 240):
            screen = self.screens[0]
            cv2.circle(screen, (y, x), r, (255, 255, 0), thikness)
            return self.screens
        # first screen
        # origin at top right corner
        # y - to the left, x - to us
        elif (x >= 240) and (y < 240):
            screen = self.screens[1]
            screen_height = screen.shape[1]
            cv2.circle(screen, (screen_height - (x - 240), y), r, (255, 255, 0), thikness)
            return self.screens
        # second screen
        # origin at lower left corner
        # x - upwards, y - to the right
        elif (x < 240) and (y >= 240):
            screen = self.screens[2]
            screen_height = screen.shape[1]
            cv2.circle(screen, (x, screen_height - (y - 240)), r, (255, 255, 0), thikness)
            return self.screens





