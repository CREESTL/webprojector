'''

Here should be functions for transforming object coordinates to sphero-cubic coordinates

'''


import numpy as np
import cv2

class Screen:
    def __init__(self):
        self.surface = np.zeros((240, 240, 3), np.uint8)
        self.size = 240

    # function gets a clockwise and anticlockwise neighbours of a screen
    def update_neighbours(self, modules):
        return

class Module:
    def __init__(self, num):
        self.num = num
        self.screens = [Screen().surface for i in range(3)]


    # function draws a circle using module coordinates system
    def draw_point(self, x, y):
        # zero screen
        # origin at lower right corner
        # y - upwards, x - to the left
        if (x < 240) and (y < 240):
            screen = self.screens[0]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            cv2.circle(screen, (y, x), 5, (255, 255, 0), 5)
            return self.screens
        # first screen
        # origin at top right corner
        # y - to the left, x - to us
        elif (x >= 240) and (y < 240):
            screen = self.screens[1]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            cv2.circle(screen, (screen_height - (x - 240), y), 5, (255, 255, 0), 5)
            return self.screens
        # second screen
        # origin at lower left corner
        # x - upwards, y - to the right
        elif (x < 240) and (y >= 240):
            screen = self.screens[2]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            cv2.circle(screen, (x, screen_height - (y - 240)), 5, (255, 255, 0), 5)
            return self.screens





