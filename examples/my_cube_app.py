from flask import Flask, send_file, Response, request, stream_with_context, make_response, render_template, jsonify
import zipfile
from math import fabs
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import numpy as np
import cv2
import logging
import io
import sys
import os
import random
from threading import Thread
import json

app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
log = logging.getLogger('werkzeug')
log.disabled = True

# field where the image is projected to
img = np.zeros((1920, 1440, 3), np.uint8)

return_img = True

#TODO process the image in a separate thread!
# one thread returns responses and the other changes the image

#TODO change color of a rectangle after shaking the cube

@app.route('/cube', methods=['GET', 'POST'])
def run_game():
    global return_img
    global img
    if request.method == 'POST' and return_img:
        # get the movement data from cube and that's all
        accel = request.json['modules'][0]['accel']
        gyro = request.json['modules'][0]['gyro']
        print(f"accel is {accel}")
        print(f"returning json.dumps")
        return_img = False
        return json.dumps(request.json)

    # encode the image and return it to the projector
    #output_img = img.copy()
    output_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    #cv2.imshow("rotated img", output_img)
    #cv2.waitKey()
    encode_param = []
    retval, buffer = cv2.imencode('.bmp', output_img, encode_param)
    img_io = io.BytesIO()
    with ZipFile(img_io, "w") as zip_file:
        zip_info = ZipInfo("cubenet.bmp")
        zip_info.compress_type = zipfile.ZIP_DEFLATED
        zip_info.compress_size = 1
        zip_file.writestr(zip_info, buffer)
    img_io.seek(0)

    # returning a response
    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'application/zip'
    print(f"returning image")
    return_img = True
    return response

# this thread processes the image separately from request handler
class ImgProcessor(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global img
        while True:
            cv2.rectangle(img, (420, 420), (840, 840), (255, 255, 0), -1)


if __name__ == "__main__":
    parallel_processor = ImgProcessor()
    parallel_processor.start()
    host = None
    port = 2399
    threaded = True

    app.run(host=host, port=port, threaded=threaded)