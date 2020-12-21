import http
import logging
import os
import platform
from os.path import dirname, realpath
import cv2
from flask import Flask, make_response
from turbojpeg import TurboJPEG

# общие настройки приложения
app = Flask(__name__)
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
font = cv2.FONT_HERSHEY_SIMPLEX
boundary = 'frame'  # multipart boundary
root_dir = dirname(dirname(realpath(__file__)))
turbo_jpeg = None

# загрузка tubrojpeg
try:
    if platform.system() == "Windows":
        try:
            turbo_jpeg = TurboJPEG(os.path.join(root_dir, "turbojpeg", "turbojpeg.dll"))
        except:
            turbo_jpeg = TurboJPEG(os.path.join(root_dir, "turbojpeg", "turbojpeg64.dll"))
except (FileNotFoundError, OSError):
    pass

# размер одного малого куба
SSP = 240

# функция рисует изображение на сторону большого куба
def draw_side(side: str):
    if side == "front":
        img = cv2.imread("mario.jpg")
        img = cv2.resize(img, (SSP * 2, SSP * 2))
        return img
    return None


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

if __name__ == '__main__':

    log = logging.getLogger('werkzeug')
    log.disabled = True

    host = None
    port = 2399
    threaded = True

    app.run(host=host, port=port, threaded=threaded)
