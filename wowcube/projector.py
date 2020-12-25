#!/usr/bin/env python3
"""
Author: Ivan Stepanov <ivanstepanovftw@gmail.com>
"""
from typing import List, Tuple
import json


class Screen:
    sid: int
    module: 'Module'  # Parent
    top: 'Screen'  # Top neighbor screen of this screen
    left: 'Screen'  # Left neighbor screen or this screen

    # noinspection PyTypeChecker
    def __init__(self, top: List[int], left: List[int]):
        self.top = top
        self.left = left

    def __repr__(self):
        return f"Screen(mid={self.module.mid}, sid={self.sid}, top=Screen(mid={self.top.module.mid}, sid={self.top.sid}), left=Screen(mid={self.left.module.mid}, sid={self.left.sid}))"

    def accel(self) -> Tuple[float, float, float]:
        x = self.module.accel[(2 + self.sid) % 3] * (1 if ((2 + self.sid) % 3) != 1 else -1)
        y = self.module.accel[(1 + self.sid) % 3] * (1 if ((1 + self.sid) % 3) != 1 else -1)
        z = self.module.accel[(0 + self.sid) % 3] * (1 if ((0 + self.sid) % 3) != 1 else -1)
        return x, y, z


class Module:
    mid: int  # Module ID
    wowcube: 'WOWCube'  # Parent
    accel: Tuple[float, float, float]  # Accelerometer
    gyro: Tuple[float, float, float]  # Gyroscope
    screens: List[Screen]

    def __init__(self, accel: Tuple[float, float, float], gyro: Tuple[float, float, float], screens: List[Screen]):
        self.accel = accel
        self.gyro = gyro
        self.screens = screens


class WOWCube:
    DEFAULT: 'WOWCube'
    modules: List[Module]

    def __init__(self, modules: List[Module]):
        super().__init__()
        self.modules = modules


    def _repair(self) -> 'WOWCube':
        # Fix accel and gyro in each Module
        for mid in range(len(self.modules)):
            self.modules[mid].accel = tuple(map(float, self.modules[mid].accel))
            self.modules[mid].gyro = tuple(map(float, self.modules[mid].gyro))
        # Assign mid to each Module
        for mid in range(len(self.modules)):
            self.modules[mid].mid = mid
        # Assign sid and parent for each Screen
        for mid in range(len(self.modules)):
            for sid in range(len(self.modules[mid].screens)):
                self.modules[mid].screens[sid].sid = sid
                self.modules[mid].screens[sid].module = self.modules[mid]
        # Assign references for each Screen
        for mid in range(len(self.modules)):
            for sid in range(len(self.modules[mid].screens)):
                self.modules[mid].screens[sid].top = self.modules[self.modules[mid].screens[sid].top[0]].screens[
                    self.modules[mid].screens[sid].top[1]]
                self.modules[mid].screens[sid].left = self.modules[self.modules[mid].screens[sid].left[0]].screens[
                    self.modules[mid].screens[sid].left[1]]
        return self

    @staticmethod
    def json_hook(obj):
        if 'top' in obj:
            #obj is {'top': [4, 2], 'left': [2, 2]}
            return Screen(**obj)
        if 'screens' in obj:
            return Module(**obj)
        else:
            print('obj in hook is ')
            print(obj)
        return WOWCube(**obj)._repair()

    @staticmethod
    def from_json(s) -> 'WOWCube':
        return json.loads(s, object_hook=WOWCube.json_hook)


_data = '''{"modules":[{"screens":[{"top":[3,0],"left":[1,0]},{"top":[1,2],"left":[5,2]},{"top":[5,1],"left":[3,1]}],"accel":["-0.00","9.81","-0.00"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[0,0],"left":[2,0]},{"top":[2,2],"left":[4,2]},{"top":[4,1],"left":[0,1]}],"accel":["-0.00","0.00","-9.81"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[1,0],"left":[3,0]},{"top":[3,2],"left":[7,2]},{"top":[7,1],"left":[1,1]}],"accel":["-0.00","-9.81","-0.00"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[2,0],"left":[0,0]},{"top":[0,2],"left":[6,2]},{"top":[6,1],"left":[2,1]}],"accel":["-0.00","0.00","9.81"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[7,0],"left":[5,0]},{"top":[5,2],"left":[1,2]},{"top":[1,1],"left":[7,1]}],"accel":["-0.00","9.81","-0.00"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[4,0],"left":[6,0]},{"top":[6,2],"left":[0,2]},{"top":[0,1],"left":[4,1]}],"accel":["-0.00","0.00","-9.81"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[5,0],"left":[7,0]},{"top":[7,2],"left":[3,2]},{"top":[3,1],"left":[5,1]}],"accel":["-0.00","-9.81","-0.00"],"gyro":["0.00","0.00","0.00"]},{"screens":[{"top":[6,0],"left":[4,0]},{"top":[4,2],"left":[2,2]},{"top":[2,1],"left":[6,1]}],"accel":["-0.00","-0.00","9.81"],"gyro":["0.00","0.00","0.00"]}]}'''
WOWCube.DEFAULT = WOWCube.from_json(_data)


def _test_json():
    wow: WOWCube = WOWCube.DEFAULT
    print(wow.modules[0].accel)  # (-0.0, 9.81, -0.0)
    print(wow.modules[0].gyro)  # (0.0, 0.0, 0.0)
    print(wow.modules[0].screens[0])  # Screen(mid=0, sid=0, top=Screen(mid=3, sid=0), left=Screen(mid=1, sid=0))
    print(wow.modules[0].screens[0].top)  # Screen(mid=3, sid=0, top=Screen(mid=2, sid=0), left=Screen(mid=0, sid=0))


if __name__ == '__main__':
    _test_json()
