from flask import Flask,request, make_response
import numpy as np
from turbojpeg import TurboJPEG
import cv2
import logging
from threading import Thread
import json

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

# a list of all modules of a cube
modules = []

@app.route('/modules', methods=['GET', 'POST'])
def run_game():
    modules = []
    global return_img
    global img
    if request.method == 'POST' and return_img:
        # adding each module info to the list
        for i in range(8):
            modules.append(request.json['modules'][i])
        return_img = False
        print("modules are")
        for m in modules:
            print(m)
        print("==========\n")
        #return json.dumps(request.json)
    return_img = True
    return json.dumps(request.json)


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