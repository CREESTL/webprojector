from flask import Flask, send_file, Response, request, stream_with_context, make_response, render_template, jsonify
import zipfile
from os.path import dirname, realpath
from math import fabs
import platform
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import numpy as np
from turbojpeg import TurboJPEG
import cv2
import logging
import io
import sys
import os
import random
from threading import Thread
import json

# basic Flask settings
app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
log = logging.getLogger('werkzeug')
log.disabled = True


# field where the image is projected to
# it has to be exactly 1920x1440
img = np.zeros((1920, 1440, 3), np.uint8)

# switch that shows whether we need to return and image or just get data from cube's sensors
return_img = True
# used to detect if cube is moving
prev_accel = None
# choice of cube side colors
color_choice = [(255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
# number of chosen color
color_num = 0
# acceleration of a cube
accel = 0
# is True if the cube is currently being moved
cube_moving = False
# is True if the cube stopped moving (not if it's just standing still for a long time)
cube_stopped = False


@app.route('/cube', methods=['GET', 'POST'])
def run_game():
    global return_img
    global img
    global prev_accel
    global accel
    global cube_moving
    global cube_stopped
    if request.method == 'POST' and return_img:
        if accel:
            prev_accel = accel
        # get the movement data from cube and that's all
        accel = request.json['modules'][0]['accel']
        # detect cube movement
        if accel != prev_accel:
            cube_moving = True
        else:
            if cube_moving:
                # the cube is not moving anymore
                cube_moving = False
                cube_stopped = True
        return_img = False
        return json.dumps(request.json)

    # encode the image and return it to the projector
    output_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # flat image of a cube (for debug)
    cv2.imwrite("flat.jpg", output_img)
    # encoding and image to pass it inside the response
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, 95]
    buffer = cv2.imencode('.jpg', output_img, encode_param)[1].tobytes()
    response = make_response(buffer)
    response.headers['Content-Type'] = 'image/jpeg'
    return_img = True
    return response

# this thread processes the image separately from request handler
class ImgProcessor(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global img
        global cube_moving
        global cube_stopped
        global color_num
        # default color (black)
        color = (0, 0, 0)
        while True:
            # choosing color only after cube stopped moving (once)
            if cube_stopped:
                color_num += 1
                if color_num > len(color_choice) - 1:
                    color_num = 0
                color = color_choice[color_num]
                cube_stopped = False
            # x axis goes upward, y axis goes to the right
            # the origin is at (480, 0)
            # left side
            cv2.rectangle(img, (480, 0), (960, 480), color, -1)
            # front side
            cv2.rectangle(img, (480, 480), (960, 960), color, -1)
            # right side
            cv2.rectangle(img, (480, 960), (960, 1440), color, -1)
            # back side
            cv2.rectangle(img, (480, 1440), (960, 1920), color, -1)
            # up side
            cv2.rectangle(img, (960, 480), (1440, 960), color, -1)
            # down side
            cv2.rectangle(img, (480, 480), (0, 960), color, -1)


if __name__ == "__main__":

    # starting a thread that constantly draws image on cube sides
    # independently from request handler
    parallel_processor = ImgProcessor()
    parallel_processor.start()

    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)