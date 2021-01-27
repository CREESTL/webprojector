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


    def move_point(self, cur_x, cur_y, screen_num):
        if screen_num == 0:
            new_x = cur_x + 10
            new_y = cur_y + 0
            return new_x, new_y
        elif screen_num == 1:
            new_x = - cur_y
            new_y = cur_x
            return new_x, new_y

    # those x and y are relative to module coordinate system
    def draw_point(self, x, y):
        # zero screen
        # origin at lower right corner
        # y - upwards, x - to the left
        if (x < 240) and (y < 240):
            screen = self.screens[0]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            #cv2.circle(screen, (5, 120), 5, (255, 255, 0), 5)
            cv2.circle(screen, (y, x), 5, (255, 255, 0), 5)
            return self.screens
        # first screen
        # origin at top right corner
        # y - to the left, x - to us
        elif (x >= 240) and (y < 240):
            screen = self.screens[1]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            cv2.circle(screen, (y, x), 5, (255, 255, 0), 5)
            return self.screens
        # second screen
        elif (x < 240) and (y >= 240):
            screen = self.screens[2]
            screen_width = screen.shape[0]
            screen_height = screen.shape[1]
            cv2.circle(screen, (y, x), 5, (255, 255, 0), 5)
            return self.screens





