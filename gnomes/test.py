from flask import Flask, request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.cube import Cube
import tracemalloc

'''

Just a circle moving through all 3 screens of a module in a circular path

'''

# basic Flask settings
app = Flask(__name__)
app.secret_key = "cube"
app.config.update(
    FAKE_LATENCY_BEFORE=1,
)
app.debug = True
log = logging.getLogger('werkzeug')
log.disabled = True


# function is used for debug
# in draws all axes, number of module and number of screen of the module
@app.route('/test', methods=['GET', 'POST'])
def draw_coords():

    # tracing the amount of used memory
    tracemalloc.start()

    cube = Cube()
    # images to be put it zip archive
    images = []
    # with each request we MUST update positions of modules of the cube
    cube.update_grid(request)

    for module in range(cube.num_modules):
        for screen in range(3):
            img = np.zeros((240, 240, 3), np.uint8)
            img = cv2.putText(img, f'm: {module} s: {screen}', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
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

    # DEFAULT POSITIONS OF MODULES
    # front side FULLY CHECKED
    # for (0, 400, 60, 0) should return (400, 60) works
    # for (0, 400, 60, 1) should return (400, -420) works
    # for (0, 400, 60, 2) should return (-400, -60) works
    # for (0, 400, 60, 3) should return (-400, 420) works
    # for (0, 60, 400, 0) should return (60, 400) works
    # for (0, 60, 400, 1) should return (400, -60) works
    # for (0, 60, 400, 2) should return (-60, -400) works
    # for (0, 60, 400, 3) should return (-400, 60) works
    # for (0, 60, 120, 0) should return (60, 120) works
    # for (0, 60, 120, 1) should return (120, -60) works
    # for (0, 60, 120, 2) should return (-60, -120) works
    # for (0, 60, 120, 3) should return (-120, 60) works
    # for (0, 400, 420, 0) should return (400, 420) works
    # for (0, 400, 420, 1) should return (400, -60) works
    # for (0, 400, 420, 2) should return (-400, -420) works
    # for (0, 400, 420, 3) should return (-400, 60) works

    # back side FULLY CHECKED
    # for (0, 400, 60, 4) should return (-560, 60) works
    # for (0, 400, 60, 5) should return (560, 420) works
    # for (0, 400, 60, 6) should return (560, -60) works
    # for (0, 400, 60, 7) should return (-560, -420) works
    # for (0, 60, 400, 4) should return (-560, 420) works
    # for (0, 60, 400, 5) should return (560, 60) works
    # for (0, 60, 400, 6) should return (560, -420) works
    # for (0, 60, 400, 7) should return (-560, -60) works
    # for (0, 60, 120, 4) should return (-900, 120) works
    # for (0, 60, 120, 5) should return (840, 60) works
    # for (0, 60, 120, 6) should return (900, -120) works
    # for (0, 60, 120, 7) should return (-840, -60) works
    # for (0, 400, 420, 4) should return (-560, 420) works
    # for (0, 400, 420, 5) should return (560, 60) works
    # for (0, 400, 420, 6) should return (560, -420) works
    # for (0, 400, 420, 7) should return (-560, -60) works

    # DO ONE ROTATION OF LOWER HALF OF THE CUBE CLOCKWISE
    # right side FULLY CHECKED
    # for (0, 400, 60, 6) should return (-880, -60) works
    # for (0, 400, 60, 7) should return (-900, 80) works
    # for (0, 60, 400, 6) should return (-540, -400) works
    # for (0, 60, 400, 7) should return (-540, 80) works
    # for (0, 60, 120, 6) should return (-540, -120) works
    # for (0, 60, 400, 7) should return (-540, 360) works
    # for (0, 400, 420, 6) should return (-540, -400) works
    # left side FULLY CHECKED
    # for (0, 400, 60, 2) should return (80, -60) works
    # for (0, 400, 60, 3) should return (-60, -80) works
    # for (0, 60, 400, 2) should return (80, -420) works
    # for (0, 60, 400, 4) should return (-420, -80) works
    # for (0, 60, 120, 2) should return (420, -120) works
    # for (0, 60, 120, 3) should return (-420, -360) works
    # for (0, 400, 420, 2) should return (80, -420) works
    # for (0, 400, 420, 3) should return (-420, -80) works

    # DO ONE ROTATION OF THE LOWER HALF CLOCKWISE AND ONE ROTATION OF BACK HALF ANTICLOCKLWISE
    # up side FULLY CHECKED
    # for (0, 400, 60, 6) should return (-420, -400) works
    # for (0, 60, 400, 6) should return (-80, -60) works
    # for (0, 60, 120, 6) should return (-360, -60) works
    # for (0, 400, 420, 6) should return (-80, -60) works
    # down side FULLY CHECKED
    # for (0, 400, 60, 3) should return (-540, -80) works
    # for (0, 60, 400, 3) should return (-900, -80) works
    # for (0, 60, 120, 3) should return (-60, -600) works
    # for (0, 400, 420, 3) should return (-900, -80) works

    new_x, new_y = cube.recalc_coords(0, 400, 420, 3)
    print(f'new X is {new_x}, new Y is {new_y}')

    # FIXME optimize memory!!!! it crashes
    # TODO make a ball move from (0, 0) to (0, 2) horizontally

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

    # deleting cube object to free memory
    del cube

    # showing used memory
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    tracemalloc.stop()

    return response


if __name__ == "__main__":
    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)