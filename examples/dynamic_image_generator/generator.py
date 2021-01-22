import os
import random
from shutil import copyfile
import time


'''
Program displays different images onto the cube's sides using file system (FS)

Author: CREESTL (kroymw3@yandex.ru)
'''


# function returns paths to original images of numbers
def get_full_paths():
    current_dir = os.path.join(os.getcwd(), 'pics')
    names = os.listdir("./pics")
    full_paths = []
    for name in names:
        full_paths.append(os.path.join(current_dir, name))
    return full_paths


# function creates a shuffled list of new images names
# in order for the emulator to see the changes if FS
def mix_new_names():
    new_names = sorted(['up.jpg', 'down.jpg', 'front.jpg', 'back.jpg', 'left.jpg', 'right.jpg'])
    random.shuffle(new_names)
    return new_names


# function copies original images to new locations
def copy_imgs(target):
    full_paths = get_full_paths()
    new_names = mix_new_names()
    new_full_paths = []
    for name in new_names:
        new_full_paths.append(os.path.join(target, name))
    for home, new in zip(full_paths, new_full_paths):
        try:
            copyfile(home, new)
        except Exception:
            pass


# works for Windows
target = os.path.expanduser('~\Documents\WOWCube\sides')
if __name__ == '__main__':
    while True:
        copy_imgs(target)
        # the emulator max FPS is 1
        time.sleep(1)

