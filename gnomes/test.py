from flask import Flask, request, make_response
import numpy as np
import cv2
import io
import logging.handlers
from zipfile import ZipFile, ZipInfo
import zipfile
from cube import Cube
import random

'''

File used for testing and debug of cube.recalc_coords()

'''


# basic Flask settings
app = Flask(__name__)
app.secret_key = "cube"
app.config.update(
    TESTING=True,
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
)

log = logging.getLogger('werkzeug')
log.disabled = True


#=======================================================================================================================

# here will be stored coordinates of all objects (circles)
objects_coords = {0: [120, 120]}
# the very first module to start with
initial_module_num = 0
# the module where the object is currently located
initial_module = None
# previous module where the circle has been
prev_module = None

# TODO create a function that checks all directions: right, left, up, down
# TODO seems like right works correctly, but up and down...not sure

# up works wrong when moving from module 0 to module 5
# right works good only for module 0 and module 1
# left works totally wrong even for the same module (0)
# down works good only for module 0 and first screen of module 3
def move_circle(dir):
    global objects_coords
    delta = 25
    for obj_num, coords in objects_coords.items():
        x, y = coords[0], coords[1]
        if dir == 'right':
            x -= delta
            objects_coords[obj_num] = [x, y]
        elif dir == 'left':
            x += delta
            objects_coords[obj_num] = [x, y]
        elif dir == 'up':
            y += delta
            objects_coords[obj_num] = [x, y]
        elif dir == 'down':
            y -= delta
            objects_coords[obj_num] = [x, y]

# function randomly moves the circle
# the idea is that the circle starts moving at zero module, moves to the random neighbour module and so on
def make_random_movement():
    global objects_coords
    # 1 -> X increases, -1 -> X decreases, 0 -> X doesn't change (same for X)
    x_dir_choice = (-1, 0, 1)
    y_dir_choice = (-1, 0, 1)
    # how much each coordinate will be changed
    delta = 10
    x_dir = random.choice(x_dir_choice)
    y_dir = random.choice(y_dir_choice)
    for obj, coords in objects_coords.items():
        x, y = coords[0], coords[1]
        x += x_dir * delta
        y += y_dir * delta
        objects_coords[obj] = [x, y]


# function checks if the object is still on the module
def changed_module(new_x, new_y):
    if (0 <= new_x <= 480) and (0 <= new_y <= 480):
        return True
    return False


@app.route('/coords', methods=['GET', 'POST'])
# function is used to test recalculation of object coords
def module_to_module():
    global initial_module_num, initial_module, prev_module
    cube = Cube()
    # with each request we MUST update positions of modules of the cube
    cube.update_grid(request)
    # move all circles randomly
    #make_random_movement()
    move_circle(dir='up')
    if cube.grid is not None:
        # only once the very first module is initialized
        if initial_module is None:
            initial_module = cube.modules[initial_module_num]
        # all other modules of the cube
        compared_modules = []
        for module in cube.modules:
            if module.num != initial_module.num:
                compared_modules.append(module)

        # FIXME I've deleted images[] after writing all below
        # FIXME for some reason the circle is not drawing any more (even on the 0 module)
        # FIXME bug is that we don't even use images array to put them all in archive - we use screens.surfaces

        # FIXME clear_screens() doesn't work???

        # FIXME NOTE that if we keep increasing Y after moving to the new module - the circle won't keep moving
        # FIXME in straight line because axes are differently angled!!!

        # coords of all objects
        global objects_coords
        # update all screens of initial module
        # FIXME if there are two for cycles here - we will have more than 24 images - that's wrong!
        # FIXME the step() functions in cube works only for ONE object on module
        # FIXME but there can be several!
        for obj, [x, y] in objects_coords.items():
            initial_module.update_screens(x, y)

        # recalculate coordinates for each of objects for each of the rest of modules
        for obj, [x, y] in objects_coords.items():
            print(f'\n\nfor initial module {initial_module.num} coords are {x, y}')
            for compared_module in compared_modules:
                new_x, new_y = cube.recalc_coords(initial_module.num, x, y, compared_module.num)
                print(f'-- for compared module {compared_module.num} new coords are {new_x, new_y}')
                # only if new coordinates were successfully calculated - we draw the object
                if (new_x is not None) and (new_y is not None):
                    compared_module.update_screens(new_x, new_y)
                    # if the circle moved onto the other module (the new one) then we change the current module
                    if changed_module(new_x, new_y):
                        print("MOVED TO THE NEW MODULE!")
                        prev_module = initial_module
                        initial_module = compared_module
                        # and change coordinates of the object (now they are calculate relative to the new origin)
                        objects_coords[obj] = [new_x, new_y]
                        print(f'now initial module is {initial_module.num}')
                    else:
                        print("stayed on the same module")

    # put the images into the response archive
    memory_file = io.BytesIO()
    img_num = 0
    with ZipFile(memory_file, "w") as zip_file:
        #FIXME bug here: all screens are black
        for module in cube.modules:
            for screen in module.screens:
                # TODO just for debug
                cv2.imwrite('/home/creestl/programming/python_coding/wowcube/webprojector/gnomes/debug/images/%i.jpg' %img_num, screen.surface)
                output_img = screen.surface
                encode_param = []
                # encode each of 24 images
                _, buffer = cv2.imencode('.bmp', output_img, encode_param)
                # add a specific info about the module this image belongs to
                # so first 3 images go to the first module, images 4, 5, 6 - to the second etc.
                zip_info = ZipInfo("modules/" + str(module.num) + "/screens/" + str(screen.num) + ".bmp")
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                zip_info.compress_size = 1
                # insert the image into the archive
                zip_file.writestr(zip_info, buffer)
                img_num += 1
    memory_file.seek(0)
    response = make_response(memory_file.read())
    response.headers['Content-Type'] = 'application/zip'

    cube.clear_screens()

    return response


# function draws all axes, number of module and number of screen of the module
@app.route('/axes', methods=['GET', 'POST'])
def draw_coords():

    cube = Cube()
    # images to be put it zip archive
    images = []
    # with each request we MUST update positions of modules of the cube
    cube.update_grid(request)

    for module in range(cube.num_modules):
        for screen in range(3):
            img = np.zeros((240, 240, 3), np.uint8)
            img = cv2.putText(img, f'm: {module} s: {screen}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            img = cv2.rotate(img, cv2.ROTATE_180)
            if screen == 0:
                # Y axis
                img = cv2.line(img, (20, 20), (20, 240), (0, 255, 255), 10)
                # X axis
                img = cv2.line(img, (20, 20), (240, 20), (255, 255, 0), 10)
            images.append(img)
    # put the images into the response archive
    memory_file = io.BytesIO()
    img_num = 0

    # DEFAULT POSITIONS OF MODULES
    # front side FULLY CHECKED
    # for (0, 400, 60, 0) should return (400, 60) works
    # for (0, 400, 60, 1) should return (400, -420) works
    # for (0, 400, 60, 2) should return (-400, -60) works
    # for (0, 400, 60, 3) should return (-400, 420) works
    # for (0, 60, 400, 0) should return (60, 400) works
    # for (0, 60, 400, 1) should return (400, -60) works
    # for (0, 60, 400, 2) should return (-60, -400) works
    # for (0, 60, 400, 3) should return (-400, 60) works
    # for (0, 60, 120, 0) should return (60, 120) works
    # for (0, 60, 120, 1) should return (120, -60) works
    # for (0, 60, 120, 2) should return (-60, -120) works
    # for (0, 60, 120, 3) should return (-120, 60) works
    # for (0, 400, 420, 0) should return (400, 420) works
    # for (0, 400, 420, 1) should return (400, -60) works
    # for (0, 400, 420, 2) should return (-400, -420) works
    # for (0, 400, 420, 3) should return (-400, 60) works

    # back side FULLY CHECKED
    # for (0, 400, 60, 4) should return (-560, 60) works
    # for (0, 400, 60, 5) should return (560, 420) works
    # for (0, 400, 60, 6) should return (560, -60) works
    # for (0, 400, 60, 7) should return (-560, -420) works
    # for (0, 60, 400, 4) should return (-560, 420) works
    # for (0, 60, 400, 5) should return (560, 60) works
    # for (0, 60, 400, 6) should return (560, -420) works
    # for (0, 60, 400, 7) should return (-560, -60) works
    # for (0, 60, 120, 4) should return (-900, 120) works
    # for (0, 60, 120, 5) should return (840, 60) works
    # for (0, 60, 120, 6) should return (900, -120) works
    # for (0, 60, 120, 7) should return (-840, -60) works
    # for (0, 400, 420, 4) should return (-560, 420) works
    # for (0, 400, 420, 5) should return (560, 60) works
    # for (0, 400, 420, 6) should return (560, -420) works
    # for (0, 400, 420, 7) should return (-560, -60) works

    # DO ONE ROTATION OF LOWER HALF OF THE CUBE CLOCKWISE
    # right side FULLY CHECKED
    # for (0, 400, 60, 6) should return (-880, -60) works
    # for (0, 400, 60, 7) should return (-900, 80) works
    # for (0, 60, 400, 6) should return (-540, -400) works
    # for (0, 60, 400, 7) should return (-540, 80) works
    # for (0, 60, 120, 6) should return (-540, -120) works
    # for (0, 60, 400, 7) should return (-540, 360) works
    # for (0, 400, 420, 6) should return (-540, -400) works
    # left side FULLY CHECKED
    # for (0, 400, 60, 2) should return (80, -60) works
    # for (0, 400, 60, 3) should return (-60, -80) works
    # for (0, 60, 400, 2) should return (80, -420) works
    # for (0, 60, 400, 4) should return (-420, -80) works
    # for (0, 60, 120, 2) should return (420, -120) works
    # for (0, 60, 120, 3) should return (-420, -360) works
    # for (0, 400, 420, 2) should return (80, -420) works
    # for (0, 400, 420, 3) should return (-420, -80) works

    # DO ONE ROTATION OF THE LOWER HALF CLOCKWISE AND ONE ROTATION OF BACK HALF ANTICLOCKLWISE
    # up side FULLY CHECKED
    # for (0, 400, 60, 6) should return (-420, -400) works
    # for (0, 60, 400, 6) should return (-80, -60) works
    # for (0, 60, 120, 6) should return (-360, -60) works
    # for (0, 400, 420, 6) should return (-80, -60) works
    # down side FULLY CHECKED
    # for (0, 400, 60, 3) should return (-540, -80) works
    # for (0, 60, 400, 3) should return (-900, -80) works
    # for (0, 60, 120, 3) should return (-60, -600) works
    # for (0, 400, 420, 3) should return (-900, -80) works

    new_x, new_y = cube.recalc_coords(0, 400, 420, 3)
    print(f'new X is {new_x}, new Y is {new_y}')

    with ZipFile(memory_file, "w") as zip_file:
        for module in cube.modules:
            for screen in module.screens:
                output_img = screen.surface
                encode_param = []
                # encode each of 24 images
                _, buffer = cv2.imencode('.bmp', output_img, encode_param)
                # add a specific info about the module this image belongs to
                # so first 3 images go to the first module, images 4, 5, 6 - to the second etc.
                zip_info = ZipInfo("modules/" + str(module.num) + "/screens/" + str(screen.num) + ".bmp")
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                zip_info.compress_size = 1
                # insert the image into the archive
                zip_file.writestr(zip_info, buffer)
                img_num += 1
    memory_file.seek(0)
    response = make_response(memory_file.read())
    response.headers['Content-Type'] = 'application/zip'

    return response


if __name__ == "__main__":
    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(debug=True, port=port, threaded=threaded)