from flask import Flask, request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.modules_drawing import Module
from math import sin, cos, pi, radians, degrees

'''

Just a circle moving through all 3 screens of a module in a circular path

'''

# basic Flask settings
app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
log = logging.getLogger('werkzeug')
log.disabled = True

# total number of images
num_screens = 24
# total number of modules
num_modules = 8

# modules of cube are created ONCE
modules = []

fixed_x = None
radius = 120
# starting angle is 45 degrees
angle = radians(0)
# used to skip one quarter of a full circle
angle_skip = False
# angular velocity
omega = 0.3
# start position for a circle
x = 240
y = 120


# FIXME bug is when x is 220.9873370999506 y is 359.54557423057406 it checks the other if statement and goes to the other part of function and draws again on screen 2
# function changes circle's coordinates
def move_circle():
    global x, y, angle, omega, angle_skip
    # starting a new circle
    if degrees(angle) >= 360:
        angle = 0
        angle_skip = False
    # each time angle is increasing
    print(f'\n\n\nangle is {degrees(angle)}')
    if (degrees(angle + omega) >= 180) and (angle_skip is False):
        angle = radians(270)
        print(f"ZHOPA {(270 - 180) / degrees(omega)}")
        x = x + radius * omega * ((270 - 180) / degrees(omega)) * cos(angle)
        y = y + radius * omega * ((270 - 180) / degrees(omega)) * sin(angle)
        angle_skip = True
        print(f'x is {x} y is {y}')
        return x, y
    angle = angle + omega
    x = x + radius * omega * cos(angle)
    y = y + radius * omega * sin(angle)
    print(f'x is {x} y is {y}')
    return x, y


# function changes circle's coordinates
# def move_circle():
#     global x, y
#     y += 10
#     print()
#     print(f'x is {x} y is {y}')
#     return x, y

# with each request module screens are updated
def update_screens():
    global modules
    # creating 8 modules once
    if not modules:
        modules = [Module(i) for i in range(8)]
    screens = []
    x, y = move_circle()
    for module in modules:
        filled_screens = module.draw_point(x, y)
        if filled_screens:
            for screen in filled_screens:
                screens.append(screen)
        # clear all screens of the module
        module.clear_screens()
    # just to double-check that all 24 screens are present
    while len(screens) != num_screens:
        # filling up the rest of empty screens
        screens.append(np.zeros((240, 240, 3), np.uint8))
    return screens


@app.route('/test', methods=['GET', 'POST'])
def draw():
    modules = []
    img_num = 0
    # create a list of output images (8 modules * 3 images on each)
    images = update_screens()
    # put the images into the response archive
    memory_file = io.BytesIO()
    for i in range(8):
        modules.append(request.json['modules'][i])
    with ZipFile(memory_file, "w") as zip_file:
        for module in range(num_modules):
            for screen in range(num_screens // num_modules):
                output_img = images[img_num]
                encode_param = []
                # encode each of 24 images
                _, buffer = cv2.imencode('.bmp', output_img, encode_param)
                # add a specific info about the module this image belongs to
                # so first 3 images go to the first module, images 4, 5, 6 - to the second etc.
                zip_info = ZipInfo("modules/" + str(module) + "/screens/" + str(screen) + ".bmp")
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
    app.run(host=host, port=port, threaded=threaded)
