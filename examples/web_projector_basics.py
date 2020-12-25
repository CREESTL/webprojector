import http
import io
import logging
import os
import platform
import random
import time
import zipfile
from os.path import dirname, realpath
from typing import Optional
from zipfile import ZipFile, ZipInfo
import cv2
import numpy as np
from flask import Flask, Response, request, make_response
from turbojpeg import TurboJPEG

from wowcube.projector import WOWCube
from wowcube.utils.exceptions import GetOutOfLoop
from wowcube.utils.image import Image


# использовать URL: http://127.0.0.1:8080/basics/jpg

app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True


font = cv2.FONT_HERSHEY_SIMPLEX
boundary = 'frame'  # multipart boundary

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

W, H = 1920, 1440
SSP = 240  # screen size pixels

def draw_cubenet() -> np.ndarray:
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


def draw_side(side: str, wowcube: Optional[WOWCube]) -> Optional[np.ndarray]:
    if side == "front":
        img = np.zeros((SSP*2, SSP*2, 3), np.uint8)
        cv2.rectangle(img, (0, 0), (SSP*2, SSP*2), (200, 255, 255), -1)
        cv2.putText(img,
                    'Hello World2',
                    (10, 60),
                    fontFace=font,
                    fontScale=2,
                    color=(255, 10, 10),
                    thickness=2,
                    bottomLeftOrigin=False)
        return img
    return None


def draw_screen(mid: int, sid: int, wowcube: Optional[WOWCube]) -> Optional[np.ndarray]:
    ACCEL_LINE_SIZE = 8

    if wowcube is not None:
        ax, ay, az = wowcube.modules[mid].screens[sid].accel()
    else:
        ax, ay, az = random.uniform(-15, 15), random.uniform(-15, 15), random.uniform(-15, 15)

    img: Image = Image(SSP, SSP)
    img.fill((0, 0, 0))
    if az < -9:
        img.text(f'Up', (SSP/2, SSP/2))
    if az > 9:
        img.text(f'Down', (SSP/2, SSP/2))
    img.circle((SSP/2, SSP/2), 9.8*ACCEL_LINE_SIZE, (255, 255, 255))
    img.line((SSP/2, SSP/2), (SSP/2 + ax*ACCEL_LINE_SIZE, SSP/2 + ay*ACCEL_LINE_SIZE), (255, 255, 255))
    img.text(f'MID: {mid}\nSID: {sid}', (10, 10))
    if mid == 0 and sid == 0:
        print(ax, ay, az)
    return img.img


@app.route('/basics/jpg', methods=['GET', 'POST'])
def basics_jpg():
    user_agent = request.user_agent.string

    if request.method == 'POST':
        wowcube = WOWCube.from_json(request.data)
    else:
        wowcube = WOWCube.DEFAULT

    print('drawing wowcube')
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


@app.route('/basics/zip', methods=['GET', 'POST'])
def basics_zip():
    if request.method == 'POST':
        wowcube = WOWCube.from_json(request.data)
    else:
        wowcube = WOWCube.DEFAULT

    stream = io.BytesIO()
    with ZipFile(stream, "w") as zip_file:
        for mid in range(8):
            for sid in range(3):
                output_img = draw_screen(mid, sid, wowcube)
                if output_img is None:
                    continue

                encode_param = []
                retval, buffer = cv2.imencode('.bmp', output_img, encode_param)

                # zip_info = ZipInfo("cubenet.bmp")
                # zip_info = ZipInfo(f"sides/{side}.bmp")
                zip_info = ZipInfo(f"modules/{mid}/screens/{sid}.bmp")
                zip_info.date_time = time.localtime(time.time())[:6]
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                zip_info.compress_size = 1
                zip_file.writestr(zip_info, buffer)
    stream.seek(0)

    response = make_response(stream.read())
    stream.close()
    response.headers['Content-Type'] = 'application/zip'
    return response


@app.route('/basics/multipart', methods=['GET'])
def basics_multipart():
    def get_frame():
        while True:
            output_img = draw_cubenet(WOWCube.DEFAULT)
            if output_img is None:
                continue

            encode_param = []
            buffer = cv2.imencode('.bmp', output_img, encode_param)[1].tobytes()

            yield (b'--'+boundary.encode()+b'\r\n'
                   b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n'
                   b'Content-Type: image/bmp\r\n'
                   b'\r\n' + buffer + b'\r\n')

    return Response(get_frame(), mimetype=f"multipart/x-mixed-replace; boundary={boundary}")


@app.route('/basics/multipart/screen', methods=['GET'])
def basics_multipart_screen():
    def get_frame():
        try:
            while True:
                for mid in range(8):
                    for sid in range(3):
                        output_img = draw_screen(mid, sid, None)
                        if output_img is None:
                            continue

                        encode_param = []
                        buffer = cv2.imencode('.bmp', output_img, encode_param)[1].tobytes()

                        # Please, surround values with quotation mark (") in each key-value pair, e.g. key="value"
                        yield (b'--'+boundary.encode()+b'\r\n'
                               # b'Content-Disposition: form-data; name="cubenet"\r\n'
                               # b'Content-Disposition: form-data; name="sides/front"\r\n'
                               b'Content-Disposition: form-data; name="modules/' + str(mid).encode() + b'/screens/' + str(sid).encode() + b'"\r\n'
                               b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n'
                               b'Content-Type: image/bmp\r\n'
                               b'\r\n' + buffer + b'\r\n')

        except GetOutOfLoop:
            return b'--'+boundary.encode()+b'--'

    return Response(get_frame(), mimetype=f"multipart/x-mixed-replace; boundary={boundary}")


if __name__ == '__main__':

    print_fps = True

    log = logging.getLogger('werkzeug')
    log.disabled = True

    host = None
    port = 8080
    threaded = True  # TODO: Since app is threaded, it is required to use locks related to img generation

    app.run(host=host, port=port, threaded=threaded)
