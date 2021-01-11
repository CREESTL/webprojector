from flask import Flask,request, make_response
import numpy as np
from turbojpeg import TurboJPEG
import cv2
import logging
from threading import Thread
import time
import json

'''
Just a single square moving around the cube vertically
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

@app.route('/cube', methods=['GET', 'POST'])
def run_game():
    global return_img
    global img

    # encode the image and return it to the projector
    output_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # flat image of a cube (for debug)
    cv2.imwrite("flat.jpg", output_img)
    # encoding and image to pass it inside the response
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, 95]
    buffer = cv2.imencode('.jpg', output_img, encode_param)[1].tobytes()
    response = make_response(buffer)
    response.headers['Content-Type'] = 'image/jpeg'
    return_img = True
    return response

# this thread draws a moving square
class ImgProcessor(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global img

        # color of a moving square
        sq_color = (255, 255, 0)
        # color of background
        bg_color = (255, 0, 0)
        # starting position of a moving square
        start_x_pos = 480
        start_y_pos = 240
        # changing position of a moving square
        x_pos = start_x_pos
        y_pos = start_y_pos
        # length of a side of a cube
        sq_side = 100
        # previous position of a cube
        prev_x_pos = None
        prev_y_pos = None
        # the direction where the square has to move
        direction = None
        # list of previous directions
        circle = []

        # x axis goes upward, y axis goes to the right
        # the origin is at (480, 0)
        # left side
        cv2.rectangle(img, (480, 0), (960, 480), bg_color, -1)
        # front side
        cv2.rectangle(img, (480, 480), (960, 960), bg_color, -1)
        # right side
        cv2.rectangle(img, (480, 960), (960, 1440), bg_color, -1)
        # back side
        cv2.rectangle(img, (480, 1440), (960, 1920), bg_color, -1)
        # up side
        cv2.rectangle(img, (960, 480), (1440, 960), bg_color, -1)
        # down side
        cv2.rectangle(img, (480, 480), (0, 960), bg_color, -1)

        while True:

            print(f"\nx_pos {x_pos}")
            print(f"y_pos {y_pos}")
            print(f"direction {direction}\n")

            if (x_pos < 960) and (y_pos < 480):
                print("on left")
                if direction not in circle:
                    print("changing to up")
                    direction = "up"
                    circle.append(direction)
            else:
                if direction == "up":
                    direction = None

            if (x_pos > 960) and (y_pos < 960):
                print("on top")
                if direction not in circle:
                    print("changing to right")
                    x_pos = 1080
                    y_pos = 480
                    direction = "right"
                    circle.append(direction)
            else:
                if direction == "right":
                    direction = None

            if (y_pos > 960) and (x_pos > 480):
                print("on right")
                if direction not in circle:
                    print("changing to down")
                    y_pos = 1080
                    x_pos = 960 - sq_side
                    direction = "down"
                    circle.append(direction)
            else:
                if direction == "down":
                    direction = None

            if x_pos < 480:
                print("on bottom")
                if direction not in circle:
                    print("changing to left")
                    x_pos = 240
                    y_pos = 960 - sq_side
                    direction = "left"
                    circle.append(direction)
            else:
                if direction == "left":
                    direction = None

            cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
            if prev_x_pos is not None and prev_y_pos is not None:
                cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color,
                              -1)
            prev_x_pos = x_pos
            prev_y_pos = y_pos
            if direction == "up":
                x_pos += sq_side
            elif direction == "right":
                y_pos += sq_side
            elif direction == "down":
                x_pos -= sq_side
            elif direction == "left":
                y_pos -= sq_side
            if (y_pos < 480) and (x_pos < 480):
                print("cleaning!!!!!!!!!!!!")
                circle = []
                x_pos = start_x_pos
                y_pos = start_y_pos
            time.sleep(0.5)


if __name__ == "__main__":
    # starting a thread that constantly draws image on cube sides
    # independently from request handler
    parallel_processor = ImgProcessor()
    parallel_processor.start()

    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)