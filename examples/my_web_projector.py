import http
import logging
import os
import platform
from os.path import dirname, realpath
import cv2
from flask import Flask, Response, request, make_response
from turbojpeg import TurboJPEG
import numpy as np
from wowcube.projector import WOWCube

# use URL: http://127.0.0.1:2399/side

# basic settings of the app
app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
font = cv2.FONT_HERSHEY_SIMPLEX
boundary = 'frame'
root_dir = dirname(dirname(realpath(__file__)))
turbo_jpeg = None

try:
    if platform.system() == "Windows":
        try:
            turbo_jpeg = TurboJPEG(os.path.join(root_dir, "turbojpeg", "turbojpeg.dll"))
        except:
            turbo_jpeg = TurboJPEG(os.path.join(root_dir, "turbojpeg", "turbojpeg64.dll"))
except (FileNotFoundError, OSError):
    pass

# one small cube size
SSP = 240
# size of the pictire to be drawn on a large cube
W, H = 1920, 1440

# function draws a picture on one side of the cube
def draw_side(side: str):
    if side == "front":
        img = cv2.imread("pics/mario.jpg")
        img = cv2.resize(img, (SSP * 2, SSP * 2))
        return img
    return None

# function draws on all sides of the cube
def draw_cubenet():
    img = np.zeros((H, W, 3), np.uint8)
    cv2.rectangle(img, (0, 0), (W, H), (200, 255, 255), -1)
    cv2.putText(img, 'Hello World!',
                (10, 600),
                fontFace=font,
                fontScale=2,
                color=(0, 0, 0),
                thickness=2,
                bottomLeftOrigin=False)
    return img

# route for single side
@app.route('/side', methods=['GET', 'POST'])
def main():
    output_img = draw_side('front')
    if output_img is None:
        return '', http.HTTPStatus.NO_CONTENT
    buffer: bytes
    if turbo_jpeg:
        buffer = turbo_jpeg.encode(output_img, quality=95)
    else:
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, 95]
        buffer = cv2.imencode('.jpg', output_img, encode_param)[1].tobytes()
    response = make_response(buffer)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

# route for the whole cube
@app.route('/cube', methods=['GET', 'POST'])
def basics_jpg():
    # request data is similar to DEFAULT
    if request.method == 'POST':
        print("========\nPOST request got")
        print('loading cube from json')
        wowcube = WOWCube().from_json(request.data)
    else:
        print("========\nGET request got")
        print('loading default cube')
        wowcube = WOWCube().load_DEFAULT()
        print(f"wowcube type is {type(wowcube)}")


    print(f"WOWCUBE modules are {wowcube.modules}")
    output_img = draw_cubenet()

    if output_img is None:
        return '', http.HTTPStatus.NO_CONTENT

    buffer: bytes
    if turbo_jpeg:
        buffer = turbo_jpeg.encode(output_img, quality=95)
    else:
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, 95]
        buffer = cv2.imencode('.jpg', output_img, encode_param)[1].tobytes()

    response = make_response(buffer)
    response.headers['Content-Type'] = 'image/jpeg'
    return response


if __name__ == '__main__':

    log = logging.getLogger('werkzeug')
    log.disabled = True

    host = None
    port = 2399
    threaded = True

    app.run(host=host, port=port, threaded=threaded)
