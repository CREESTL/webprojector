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



    # transforms (x, y) to the number of module
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
        if (x > 0) and (x < 960):
            # right half
            module_x_range = [1, 2, 4, 7]
        elif (x >= 960) and (x < 1920):
            # left half
            module_x_range = [0, 3, 5, 6]
        elif (x < 0) and (x > -960):
            # left half
            module_x_range = [0, 3, 5, 6]
        elif (x <= -960) and (x > -1920):
            # right half
            module_x_range = [1, 2, 4, 7]
        elif x == 0:
            # all
            module_x_range = range(8)

        print(f'module_x_range = {module_x_range}')
        print(f'module_y_range = {module_y_range}')

        if (module_y_range is not None) and (module_y_range is not None):
            module_range = list(set(module_x_range) & set(module_y_range))

        return module_range

    # transforms (x, y) to coordinates of specific module
    # FIXME
    # this whole program works only for default position of modules
    # if we move the modules - it will display incorrect numbers
    # for example if we move module 0 up, module 3 will come to its place
    # but the program will still think that there is module 0 at this place
    def coords_to_module_coords(self, x, y):
        module_num = self.coords_to_module_num(x, y)
        print(f'module num is {module_num}')
        # x and y coords relative to the module
        rel_x = x % 240
        rel_y = y % 240
        print(f"rel_y = {rel_y}")
        print(f"rel_x = {rel_x}")


transformer = Transformer()
transformer.coords_to_module_coords(200, 200)