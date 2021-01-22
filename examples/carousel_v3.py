from flask import Flask,make_response
import numpy as np
import cv2
import logging
from threading import Thread
import time

'''
Two squares moving around the cube

Author: CREESTL (kroymw3@yandex.ru)
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

# this thread draws a vertically moving square
class VerticalCarousel(Thread):

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
        sq_side = 96
        # previous position of a cube
        prev_x_pos = None
        prev_y_pos = None

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

            # each of the x_pos and y_pos below in "while" conditions is a position of a left down corner of a
            # square on the cube

            # square is on the left side (of a flat cube image)
            while x_pos < 960:
                # drawing a square in it's current position
                cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
                # hiding square's previous position
                if prev_x_pos is not None and prev_y_pos is not None:
                    cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color,
                                  -1)
                # let it all render correctly
                time.sleep(0.5)
                prev_x_pos = x_pos
                prev_y_pos = y_pos
                # moving square up
                x_pos += sq_side

            # moving square to the next side
            x_pos = 1080
            y_pos = 480

            # square is on the top side (of a flat cube image)
            while y_pos < 960:
                cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
                if prev_x_pos is not None and prev_y_pos is not None:
                    cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color,
                                  -1)
                time.sleep(0.5)
                prev_x_pos = x_pos
                prev_y_pos = y_pos
                # moving square to the right
                y_pos += sq_side

            y_pos = 1080
            x_pos = 960 - sq_side

            # square is on the left right (of a flat cube image)
            while x_pos >= 480:
                cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
                if prev_x_pos is not None and prev_y_pos is not None:
                    cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color,
                                  -1)
                time.sleep(0.5)
                prev_x_pos = x_pos
                prev_y_pos = y_pos
                # moving square down
                x_pos -= sq_side

            x_pos = 240
            y_pos = 960 - sq_side

            # square is on the bottom side (of a flat cube image)
            while y_pos >= 480:
                cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
                if prev_x_pos is not None and prev_y_pos is not None:
                    cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color,
                                  -1)
                time.sleep(0.5)
                prev_x_pos = x_pos
                prev_y_pos = y_pos
                # moving square to the left
                y_pos -= sq_side

            x_pos = start_x_pos
            y_pos = start_y_pos

# this thread draws a horizontally moving square
class HorizontalCarousel(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global img

        # color of a moving square
        sq_color = (0, 0, 255)
        # color of background
        bg_color = (255, 0, 0)
        # starting position of a moving square
        x_pos = 600
        y_pos = 0
        # length of a side of a cube
        sq_side = 100
        # previous position of a cube
        prev_x_pos = None
        prev_y_pos = None

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
            # drawing a square
            cv2.rectangle(img, (x_pos, y_pos), (x_pos + sq_side, y_pos + sq_side), sq_color, -1)
            # hiding a "trace" of a square
            # drawing another square of background color on it's previous position
            if prev_x_pos is not None and prev_y_pos is not None:
                cv2.rectangle(img, (prev_x_pos, prev_y_pos), (prev_x_pos + sq_side, prev_y_pos + sq_side), bg_color, -1)
            prev_x_pos = x_pos
            prev_y_pos = y_pos
            # moving the square to the right
            y_pos += sq_side
            # need a pause to let it all render onto the cube
            time.sleep(0.3)
            # return to the start position
            if y_pos > 1920:
                y_pos = 0


if __name__ == "__main__":

    # two threads for two squares
    thread_1 = VerticalCarousel()
    thread_2 = HorizontalCarousel()

    thread_1.start()
    thread_2.start()

    host = None
    port = 2399
    threaded = True
    # starting the Flask app itself
    app.run(host=host, port=port, threaded=threaded)