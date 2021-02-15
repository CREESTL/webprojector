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



# function is used for debug
# in draws all axes, number of module and number of screen of the module
@app.route('/test', methods=['GET', 'POST'])
def draw_coords():
    # images to be put it zip archive
    images = []
    # creating a cube to work with
    cube = Cube(request)
    for module in range(cube.num_modules):
        for screen in range(3):
            img = np.zeros((240, 240, 3), np.uint8)
            img = cv2.putText(img, f'm: {module} s: {screen}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                              cv2.LINE_AA)
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

    # FIXME test this on different cases
    # DEFAULT POSITIONS OF MODULES
    # for (0, 60, 120, 4) should return (-900, 120)# works with  x = -(960 - x),  |  x, y = -x, (480 - y)  AND # works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (0, 60, 120, 5) should return (840, 60)# works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (0, 60, 120, 6) should return (60, -840)# works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (0, 60, 120, 7) should return (-840, -60)# works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (0, 60, 400, 5) should return (560, 60)# works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (0, 360, 20, 5) should return (600, 460) # works with  x = -(960 - x),  |  x, y = -x, (480 - y) AND # works with x = -(960 - x),  |   if i == 0: x, y = 960 - y, 960 + x else x, y = y, -x
    # for (1, 60, 120, 0) should return (-120, 60) # works

    # DO ONE ROTATION OF LOWER HLF OF THE CUBE TO THE RIGHT
    # for (0, 60, 120, 3) should return (-540, 360) doesn't work
    new_x, new_y = cube.recalc_pos(0, 60, 120, 3)
    print(f'new X is {new_x}, new Y is {new_y}')


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