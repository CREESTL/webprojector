from flask import Flask, send_file, Response, request, stream_with_context, make_response, render_template, jsonify
import zipfile
from math import fabs
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import numpy as np
import cv2 as cv
import io
import sys
import os
import random
from threading import Thread
import json
def collision_with_apple(apple_position, score, arr):
    a = random.randint(0, len(arr) - 1)
    b = random.randint(0, len(arr[a]) - 1)
    apple_position = arr[a][b]
    score += 1
    return [b, a], apple_position, score

def collision_with_boundaries(snake_head, boundaries):
    for i in boundaries:
        if snake_head[0] > i[0] and snake_head[0] <= i[0] + 19 and snake_head[1] > i[1] and snake_head[1] <= i[1] + 19:
            return 1
    return 0


def collision_with_self(snake_position):
    snake_head = snake_position[0]
    if snake_head in snake_position[1:]:
        return 1
    else:
        return 0

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
os.environ["SDL_VIDEO_CENTERED"] = '1'
img = np.zeros((1920, 1440, 3), np.uint8)
score = 0
prev_button_direction = 1
button_direction = 1
arr = []
for i in range(0, 1440, 20):
    b = []
    for j in range(0, 1920, 20):
        if i < 480 and j < 480 or i < 480 and j > 920 or i > 920 and j < 480 or i > 920 and j > 920:
            continue
        else:
            b.append([i, j])
    arr.append(b)
a = random.randint(0, len(arr) - 1)
b = random.randint(0, len(arr[a]) - 1)
snake_head = arr[a][b]
snake_position = []
for i in range(3):
    snake_position.append([snake_head[0], snake_head[1] + i * 10])
boundaries = []
for i in range(100):
    a = random.randint(0, len(arr) - 1)
    b = random.randint(0, len(arr[a]) - 1)
    check = True
    for j in snake_position:
        if arr[a][b][0] >= j[0] - 41 and arr[a][b][0] <= j[0] + 41 and arr[a][b][1] >= j[1] - 41 and arr[a][b][1] <= j[1] + 41:
            check = False
            break
    if check:
        boundaries.append(arr[a][b])
a = random.choice(arr)
b = random.choice(a)
a = random.randint(0, len(arr) - 1)
b = random.randint(0, len(arr[a]) - 1)
apple_position = arr[a][b]
check = True
@app.route('/cube', methods=['GET', 'POST'])
def zip():
    global check
    if request.method == 'POST' and not check:
        data = request.json['modules'][0]['accel']
        global button_direction
        x = float(data[0].replace(',', '.'))
        y = float(data[1].replace(',', '.'))
        z = float(data[2].replace(',', '.'))
        if x > -5 and x < 5:
            if y > -5 and y < 5 and z > 5:
                if fabs(x) > fabs(y):
                    if x > 0:
                        button_direction = 3
                    else:
                        button_direction = 2
                else:
                    if y > 0:
                        button_direction = 0
                    else:
                        button_direction = 1
            elif y > -5 and y < 5 and z < -5:
                if fabs(x) > fabs(y):
                    if x > 0:
                        button_direction = 2
                    else:
                        button_direction = 3
                else:
                    if y > 0:
                        button_direction = 0
                    else:
                        button_direction = 1
            elif y > 5 and z > -5 and z < 5:
                if fabs(x) > fabs(y - 10):
                    if x > 0:
                        button_direction = 0
                    else:
                        button_direction = 1
                else:
                    if z > 0:
                        button_direction = 3
                    else:
                        button_direction = 2
            elif y < -5 and z > -5 and z < 5:
                if fabs(x) > fabs(y + 10):
                    if x > 0:
                        button_direction = 1
                    else:
                        button_direction = 0
                else:
                    if z > 0:
                        button_direction = 3
                    else:
                        button_direction = 2
        else:
            if x >= 5:
                if fabs(x - 10) > fabs(y):
                    if z > 0:
                        button_direction = 2
                    else:
                        button_direction = 3
                else:
                    if y > 0:
                        button_direction = 0
                    else:
                        button_direction = 1
            else:
                if fabs(x+10) > fabs(y):
                    if z > 0:
                        button_direction = 3
                    else:
                        button_direction = 2
                else:
                    if y > 0:
                        button_direction = 0
                    else:
                        button_direction = 1

        check = True
        print("in snake return json.dumps")
        return json.dumps(request.json)
    global img
    output_img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)

    encode_param = []
    retval, buffer = cv.imencode('.bmp', output_img, encode_param)

    img_io = io.BytesIO()
    with ZipFile(img_io, "w") as zip_file:
        zip_info = ZipInfo("cubenet.bmp")
        zip_info.compress_type = zipfile.ZIP_DEFLATED
        zip_info.compress_size = 1
        zip_file.writestr(zip_info, buffer)
    img_io.seek(0)
    response = make_response(img_io.read())
    response.headers['Content-Type'] = 'application/zip'
    check = False
    print("in snake return response")
    return response


speed = 1500000
class MyThread(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        c = 0
        global speed
        while True:
            if c > speed:
                global img, apple_position, snake_head, snake_position, score, boundaries, button_direction, prev_button_direction, arr
                img = np.zeros((1920, 1440, 3), np.uint8)
                # Display Apple
                cv.rectangle(img, (apple_position[0], apple_position[1]), (apple_position[0] + 20, apple_position[1] + 20),
                             (0, 0, 255), -1)
                # Display Snake
                for position in snake_position:
                    cv.rectangle(img, (position[0], position[1]), (position[0] + 20, position[1] + 20), (0, 255, 0), -1)
                for position in boundaries:
                    cv.rectangle(img, (position[0], position[1]), (position[0] + 20, position[1] + 20), (255, 0, 0), -1)

                # 0-Left, 1-Right, 3-Up, 2-Down, q-Break
                # a-Left, d-Right, w-Up, s-Down

                prev_button_direction = button_direction
                # Change the head position based on the button direction
                if button_direction == 1:
                    snake_head[0] += 20
                    if snake_head[0] > 960 and snake_head[1] < 480:
                        snake_head = [1440 - snake_head[1], 480]
                        button_direction = 2
                    elif snake_head[0] > 1440 and 960 >= snake_head[1] > 480:
                        snake_head = [960, 2400 - snake_head[1]]
                        button_direction = 0
                    elif snake_head[0] > 960 and 1440 > snake_head[1] > 960:
                        snake_head = [snake_head[1], 960]
                        button_direction = 3
                    elif snake_head[0] > 960 and 1920 > snake_head[1] > 1440:
                        snake_head = [1440, 2400 - snake_head[1]]
                        button_direction = 0
                elif button_direction == 0:
                    snake_head[0] -= 20
                    if snake_head[0] < 480 and snake_head[1] < 480:
                        snake_head = [snake_head[1], 480]
                        button_direction = 2
                    elif snake_head[0] < 0 and 960 >= snake_head[1] > 480:
                        snake_head = [480, 2400 - snake_head[1]]
                        button_direction = 1
                    elif snake_head[0] < 480 and 1440 > snake_head[1] > 960:
                        snake_head = [1440 - snake_head[1], 960]
                        button_direction = 3
                    elif snake_head[0] < 480 and 1920 > snake_head[1] > 1440:
                        snake_head = [0, 2400 - snake_head[1]]
                        button_direction = 1
                elif button_direction == 2:
                    snake_head[1] += 20
                    if snake_head[1] > 960 and snake_head[0] < 480:
                        snake_head = [480, 1440 - snake_head[0]]
                        button_direction = 1
                    elif snake_head[1] > 960 and snake_head[0] > 960:
                        print(snake_head)
                        snake_head = [960, snake_head[0]]
                        button_direction = 0
                elif button_direction == 3:
                    snake_head[1] -= 20
                    if snake_head[1] < 480 and snake_head[0] < 480:
                        snake_head = [480, snake_head[0]]
                        button_direction = 1
                    elif snake_head[1] < 480 and snake_head[0] > 960:
                        snake_head = [960, 1440 - snake_head[0]]
                        button_direction = 0
                snake_head[1] %= 1920

                # Increase Snake length on eating apple
                if snake_head[0] >= apple_position[0] and snake_head[0] <= apple_position[0] + 20 and snake_head[1] >= \
                        apple_position[1] and snake_head[1] <= apple_position[1] + 20:
                    speed //= 2
                    end, apple_position, score  = collision_with_apple(apple_position, score, arr)
                    snake_position.insert(0, list(snake_head))

                else:
                    snake_position.insert(0, list(snake_head))
                    snake_position.pop()

                # On collision kill the snake and print the score
                if collision_with_boundaries(snake_head, boundaries) == 1 or collision_with_self(snake_position) == 1:
                    print("DIE")

                c = 0
            c += 1


def create_threads():
    my_thread = MyThread()
    my_thread.start()

create_threads()

host = None
port = 2399
threaded = True

app.run(host=host, port=port, threaded=threaded)