'''

Here should be functions for transforming object coordinates to sphero-cubic coordinates

'''

class Transformer:
    def __init__(self):
        self.max_x = 1920
        self.max_y = 1920
        self.num_screens = 24
        self.num_modules = 8
        self.screens_per_module = self.num_screens // self.num_modules
         #
         # if y < 0 -> 1 2 3 4 else 5 6 7 8
         # if x < 0 -> 1 4 6 7 else 2 3 5 8
         #
    def coords_to_module_num(self, x, y):
        # x goes to the right
        # y goes to us
        module_num = None
        module_x_range = None
        module_y_range = None
        module_range = None
        if y >= 1920:
            y = y - 1920
        if y <= -1920:
            y = y + 1920
        if (y > 0) and (y < 480):
            # front half, upper side
            module_y_range = [0, 1]
        elif (y >= 480) and (y < 960):
            # front half, down side
            module_y_range = [2, 3]
        elif (y >= 960) and (y < 1440):
            # back half down side
            module_y_range = [6, 7]
        elif (y >= 1440) and (y < 1920):
            # back half, upper side
            module_y_range = [4, 5]
        elif (y < 0) and (y > -480):
            # back half, upper side
            module_y_range = [4, 5]
        elif (y <= -480) and (y > -960):
            # back half down side
            module_y_range = [6, 7]
        elif (y <= -960) and (y > -1440):
            # front half, down side
            module_y_range = [2, 3]
        elif (y <= -1440) and (y > -1920):
            # front half, upper side
            module_y_range = [0, 1]
        elif y == 0:
            # all
            module_y_range = range(8)


        if x >= 1920:
            x = x - 1920
        if x <= -1920:
            x = x + 1920
        if (x > 0) and (x < 480):
            # right half, upper side
            module_x_range = [1, 4]
        elif (x >= 480) and (x < 960):
            # right half, down side
            module_x_range = [2, 7]
        elif (x >= 960) and (x < 1440):
            # left half down side
            module_x_range = [3, 6]
        elif (x <= -1440) and (x > -1920):
            # left half, upper side
            module_x_range = [0, 5]
        elif (x < 0) and (x > -480):
            module_x_range = [0, 5]
        elif (x <= -480) and (x > -960):
            module_x_range = [3, 6]
        elif (x <= -960) and (x > -1440):
            module_x_range = [2, 7]
        elif (x <= -1440) and (x > -1920):
            module_x_range = [1, 4]
        elif x == 0:
            # all
            module_x_range = range(8)

        print(f'module_x_range = {module_x_range}')
        print(f'module_y_range = {module_y_range}')

        if (module_y_range is not None) and (module_y_range is not None):
            module_range = list(set(module_x_range) & set(module_y_range))

        return module_range


transformer = Transformer()
print(transformer.coords_to_module_num(200, 490))