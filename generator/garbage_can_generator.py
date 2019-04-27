import pandas as pd
import numpy as np

from bmob import *
from bmob_beans import GarbageCan

b = Bmob("cc9b6713ae4044193269990fede0c4f3", "1728823c0ecc355d0898ea9e836b03ce")


def insert(garbage_can):
    data_dic = {
        'areaCode': garbage_can.area_code,
        'blockCode': garbage_can.block_code,
        'number': garbage_can.number,
        'latitude': garbage_can.latitude,
        'longitude': garbage_can.longitude,
        'maxVolume': garbage_can.max_volume
    }
    b.insert(
        'GarbageCan',
        data_dic
    )


def build_garbage_can(number,
                      latitude,
                      longitude
                      ):
    garbage_can = GarbageCan({})
    garbage_can.area_code = '360112'
    garbage_can.block_code = '101'
    garbage_can.number = number
    garbage_can.latitude = latitude
    garbage_can.longitude = longitude
    garbage_can.max_volume = 40000
    return garbage_can


if __name__ == '__main__':
    number = 30
