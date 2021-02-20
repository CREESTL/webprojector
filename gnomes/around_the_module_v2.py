from flask import Flask, request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.cube import Cube
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


radius = 120
# starting angle is 45 degrees
angle = radians(0)
# used to skip one quarter of a full circle
angle_skip = False
# angular velocity
# 17.2 degrees
omega = 0.3
# start position for a circle
x = 240
y = 120


# function changes circle's coordinates
def move_circle():
    global x, y, angle, omega, angle_skip
    # starting a new circle
    if degrees(angle) >= 360:
        angle = 0
        angle_skip = False
    # we should avoid using angles between 180 and 270 degrees so we skip them
    if (degrees(angle + omega) >= 270) and (angle_skip is False):
        # and make angle more than 270
        while degrees(angle) <= 360:
            angle = angle + omega
            # also calculate new x and y for the skip
            x = x + radius * omega * cos(angle)
            y = y + radius * omega * sin(angle)
        # we only do it once in a round
        angle_skip = True
        return x, y
    # if angle is not between 180 and 270 - everything is much more simple
    angle = angle + omega
    x = x + radius * omega * cos(angle)
    y = y + radius * omega * sin(angle)
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