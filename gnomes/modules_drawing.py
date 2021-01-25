from flask import Flask,request, make_response
import numpy as np
from turbojpeg import TurboJPEG
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
from threading import Thread
import json
#from coords_transform import Transformer
'''

Drawing each module with different color 
Understanding the modules coordinates 

'''

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
# choice of cube side colors
color_choice = [(255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
# number of chosen color
color_num = 0

# total number of images
num_screens = 24
# total number of modules
num_modules = 8

# a list of all modules of a cube
modules = []

def create_images():
    images = []
    for i in range(num_screens):
        img = np.zeros((240, 240, 3), np.uint8)
        cv2.rectangle(img, (0, 0), (240, 240), (255, 255, 0), -1)
        cv2.putText(img, str(i), (120, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        images.append(img)
    return images

# draws plain green modules correctly
@app.route('/test', methods=['GET', 'POST'])
def draw():
    modules = []
    img_num = 0
    # create a list of output images (8 modules * 3 images on each)
    images = create_images()
    # put the images into the response archive
    memory_file = io.BytesIO()
    for i in range(8):
        modules.append(request.json['modules'][i])
    print("modules are")
    for i, m in enumerate(modules):
        print(f'module {i} {m}')
    print("==========\n")
    with ZipFile(memory_file, "w") as zip_file:
        for module in range(num_modules):
            for screen in range(num_screens // num_modules):
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


# this thread processes the image separately from request handler
class draw_modules(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global img
        global color_num
        global color_choice
        # default color (black)
        color = (0, 0, 0)
        while True:
            # choosing color only after cube stopped moving (once)
            color_num += 1
            if color_num > len(color_choice) - 1:
                color_num = 0
            color = color_choice[color_num]
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
    module_drawer = draw_modules()
    module_drawer.start()

    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)