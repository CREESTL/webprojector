from flask import Flask,request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.modules import Module
from math import sin,cos,pi, radians

'''

Just a circle moving through all 3 screens of a module in straight line

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


# for drawing a circle
x = 120
y = 120
direction = 'up'


# function changes circle's coordinates (goes from screen 0
def move_circle():
    global x, y, direction
    if direction == 'up':
        y += 10
        if y >= 360:
            direction = 'left'
        return x, y
    if direction == 'left':
        # remember the last y position so that circle can move straight down
        x += 10
        if x >= 360:
            direction = 'right'
        return x, y
    if direction == 'right':
        x -= 10
        if x <= 120:
            direction = 'down'
        return x, y
    if direction == 'down':
        y -= 10
        if y <= 120:
            direction = 'up'
        return x, y


# function forms a table of relative positions of module
def form_trbl(req):
    trbl = []
    for i in range(8):
        trbl.append(req.json['modules'][i])
    return trbl


# function forms a list of modules
def form_modules(req):
    modules = []
    # creating a table of relative positions
    trbl = form_trbl(req)
    for i, module in enumerate(trbl):
        modules.append(Module(i, trbl))
    return modules


# with each request module screens are updated
def update_screens(modules):
    screens = []
    # getting new scubic X and Y coordinates of an object
    x, y = move_circle()
    for module in modules:
        # move the object to the new scubic coordinates
        module.move(x, y)
        # draw an object on those coordinates
        filled_screens = module.draw_point()
        if filled_screens:
            for screen in filled_screens:
                screens.append(screen)
        # clear all screens of the module to render on them again later
        module.clear_screens()
    # just to double-check that all 24 screens are present
    while len(screens) != num_screens:
        # filling up the rest of empty screens
        screens.append(np.zeros((240, 240, 3), np.uint8))
    return screens


@app.route('/test', methods=['GET', 'POST'])
def draw():
    img_num = 0
    # creating 8 modules
    modules = form_modules(request)
    # create a list of output images (8 modules * 3 images on each)
    images = update_screens(modules)
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