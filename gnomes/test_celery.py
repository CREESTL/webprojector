from flask import Flask, request, make_response
import numpy as np
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from gnomes.cube import Cube
import tracemalloc
import time
import redis
from gnomes.flask_celery import make_celery
from celery import Celery
'''

File used for testing and debug of cube.recalc_coords()

'''



# Start Redis server with
# 1) cd redis
# 2) redis-server redis.windows.conf

# Start Celery with
# 1) cd webprojector
# 2) celery -A gnomes.test.celery worker

# basic Flask settings
app = Flask(__name__)
app.secret_key = "cube"
app.config.update(
    TESTING=True,
    SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/',
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_BACKEND='redis://localhost:6379'
)
r = redis.Redis(host='localhost', port=6379)
celery = make_celery(app)

log = logging.getLogger('werkzeug')
log.disabled = True


#=======================================================================================================================


# start position for a circle
x = 240
y = 120
direction = 1
cube = Cube()

# function changes circle's coordinates
def move_circle():
    global x, y, direction
    if direction == 1:
        x -= 10
        if x <= -240:
            direction = 0
    elif direction == 0:
        x += 10
        if x >= 240:
            direction = 1
    return x, y


# TODO Do I need Celery? It doesn't seem to help prevent freezes
# TODO Gunicorn is not supported for windows


# function is used to test recalculation of object coords
# FIXME function is too heavy
@app.route('/coords', methods=['GET', 'POST'])
@celery.task(name='test.module_to_module')
def module_to_module():
    start_time = time.time()
    # tracing the amount of used memory
    tracemalloc.start()
    global cube
    # images to be put it zip archive
    images = []
    # with each request we MUST update positions of modules of the cube
    cube.update_grid(request)
    x, y = move_circle()
    for img in cube.modules[0].update_screens(x, y):
        images.append(img)
    new_x, new_y = cube.recalc_coords(0, x, y, 1)
    #print(f'new_x is {new_x}, new_y is {new_y}')
    for img in cube.modules[1].update_screens(new_x, new_y):
        images.append(img)
    while len(images) != 24:
        images.append(np.zeros((240, 240, 3), np.uint8))

    # FIXME optimize memory!!!! When circle suddenly stops moving - RAM rising 100mb each second
    # FIXME if I start rotating the half of cube many times - circle stops maybe because module_to_module() has not
    # FIXME enough time to process what's happening


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

    # deleting cube object to free memory
    #del cube
    cube.clear_screens()

    # showing used memory
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    tracemalloc.stop()
    print(f'time of handling request: {time.time() - start_time}')
    return response


# function draws all axes, number of module and number of screen of the module
@app.route('/axes', methods=['GET', 'POST'])
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
    #app.run(host=host, port=port, threaded=threaded, debug=True)
    app.run(debug=True, port=port)