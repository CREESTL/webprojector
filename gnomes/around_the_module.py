from flask import Flask,request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.cube import Cube
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



@app.route('/test', methods=['GET', 'POST'])
def draw():
    # moving the object with each request
    x, y = move_circle()
    # images to be put it zip archive
    images = []
    # creating a cube to work with
    cube = Cube()
    cube.update_grid(request)
    # all modules of the cube
    modules = cube.modules
    for module in modules:
        for img in module.update_screens(x, y):
            images.append(img)
    # put the images into the response archive
    memory_file = io.BytesIO()
    img_num = 0
    with ZipFile(memory_file, "w") as zip_file:
        for module in range(cube.num_modules):
            for screen in range(cube.num_screens // cube.num_modules):
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