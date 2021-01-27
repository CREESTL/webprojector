from flask import Flask,request, make_response
import numpy as np
from turbojpeg import TurboJPEG
import cv2
import io
import logging
from zipfile import ZipFile, ZipInfo
import zipfile
import json
from gnomes.modules_drawing import Module
import time

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


# total number of images
num_screens = 24
# total number of modules
num_modules = 8

# a list of all modules of a cube
modules = []

# def create_images():
#     images = []
#     for i in range(num_screens):
#         img = np.zeros((240, 240, 3), np.uint8)
#         cv2.rectangle(img, (0, 0), (240, 240), (255, 255, 0), -1)
#         cv2.putText(img, str(i), (120, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
#         images.append(img)
#     return images

x, y = 0, 120
def update_screens():
    global x, y
    module_0 = Module(0)
    module_1 = Module(1)
    screens = []
    # 3 used screens of module (object could be just on one of them)
    filled_screens_0 = module_0.draw_point(120, 360)
    filled_screens_1 = module_1.draw_point(294, 120)
    screens = filled_screens_0 + filled_screens_1
    while len(screens) != num_screens:
        screens.append(np.zeros((240, 240, 3), np.uint8))
    return screens



# draws plain green modules correctly
@app.route('/test', methods=['GET', 'POST'])
def draw():
    modules = []
    img_num = 0
    # create a list of output images (8 modules * 3 images on each)
    images = update_screens()

    # put the images into the response archive
    memory_file = io.BytesIO()
    for i in range(8):
        modules.append(request.json['modules'][i])
    # for i, m in enumerate(modules):
    #     print(f'MODULE {i}')
    #     for j, s in enumerate(m['screens']):
    #         print(f'--screen {j}')
    #         print(f'----counter clockwise: module {s["top"][0]} screen {s["top"][1]}')
    #         print(f'----clockwise: module {s["left"][0]} screen {s["left"][1]}')
    # print("==========\n")
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




if __name__ == "__main__":

    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)