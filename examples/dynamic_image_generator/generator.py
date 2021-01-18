import os
import random
from shutil import copyfile
import time

# функция возвращает пути к исходным фото
def get_full_paths():
    current_dir = os.path.join(os.getcwd(), 'pics')
    names = os.listdir("./pics")
    full_paths = []
    for name in names:
        full_paths.append(os.path.join(current_dir, name))
    return full_paths

# фукнция создает список названий новых фото (расположены в произвольном порядке)
def mix_new_names():
    new_names = sorted(['up.jpg', 'down.jpg', 'front.jpg', 'back.jpg', 'left.jpg', 'right.jpg'])
    random.shuffle(new_names)
    return new_names

# функция копирует исходные фото по новым путям
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

target = r'C:\Users\Dan\Documents\WOWCube\sides'
if __name__ == '__main__':
    while True:
        copy_imgs(target)
        # эмулятор выдает максимум 1fps - подстраиваемся под эту величину
        time.sleep(1)

