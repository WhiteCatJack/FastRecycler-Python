import datetime
from decimal import Decimal

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bmob import *

b = Bmob("cc9b6713ae4044193269990fede0c4f3", "1728823c0ecc355d0898ea9e836b03ce")


class Data:
    ID_LIST = [
        '2f018a22cd', '88a57f17a4', '146dfb2f04', 'd9f718bd5b', 'ff0c7d69a8', 'fa1c5b819b',
        '7946f9d5ad', '025dde8c81', '0c70e8ab2c', '58ed092e18', 'cc997b8e96', '17d56d79f7',
        '8451eb1f52', '9989db9f62', '76215b063c', '1e5cdfca36', '22d974295e', 'c436fde6fc',
        '8a2921ff55', '5e47629b6f', 'f4c17c6967', '0UbuZTTZ', 'e7ff0efbf7', '9d650e75ea',
        'e0b33013eb', '03f0647ad4', '9025da459f', '7e0e3c6f5b', '12eec8eb5b'
    ]
    HEAT_3 = 25
    HEAT_2 = 10
    HEAT_1 = 2
    HOT_3_LIST = [7, 8, 10, 21]
    HOT_2_LIST = [24, 25, 26, 27, 28]
    HOT_1_LIST = [1, 2, 3, 4, 5, 6, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 29]

    MEAL_TIME_PERIOD = [
        [[7, 30], [8, 30]],
        [[11, 30], [12, 30]],
        [[17, 30], [18, 30]]
    ]
    SLEEP_TIME_PERIOD = [
        [[22, 30], [23, 59]],
        [[0, 0], [6, 30]],
    ]
    RECYCLE_TIME = [
        [7, 30],
        [10, 30],
        [12, 30],
        [15, 30],
        [18, 30],
        [20, 0]
    ]

    DEFAULT_DATA_TIME_PERIOD_IN_MINUTE = 10
    PRECISION = '0.000000'
    MAX_VOLUME = 40000


class Utils:
    @staticmethod
    def get_garbage_can_id(number):
        return Data.ID_LIST[number - 1]

    @staticmethod
    def get_formatted_time(year, month, day, hour, minute):
        return str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + \
               str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':00'

    @staticmethod
    def random_0_1():
        return np.random.random()


class Slope:
    HEAT_SLOPE_DICT = {
        Data.HEAT_3: 9,
        Data.HEAT_2: 3,
        Data.HEAT_1: 1
    }

    @staticmethod
    def get_heat_level(number):
        if number in Data.HOT_3_LIST:
            return Data.HEAT_3
        elif number in Data.HOT_2_LIST:
            return Data.HEAT_2
        else:
            return Data.HEAT_1

    @staticmethod
    def __is_work_day__(weekday):
        return 0 <= weekday <= 4

    @staticmethod
    def __judge_time_in_period(hour, minute, period_list):
        for time_period in period_list:
            left = time_period[0]
            right = time_period[1]
            if left[0] <= hour <= right[0] and left[1] <= minute <= right[1]:
                return True
        return False

    @staticmethod
    def __is_meal_time__(hour, minute):
        return Slope.__judge_time_in_period(hour, minute, Data.MEAL_TIME_PERIOD)

    @staticmethod
    def __is_sleep_time__(hour, minute):
        return Slope.__judge_time_in_period(hour, minute, Data.SLEEP_TIME_PERIOD)

    @staticmethod
    def __get_random__():
        return -1 + Utils.random_0_1() * 2

    @staticmethod
    def get_slope(heat_level, weekday, hour, minute):
        slope = Slope.HEAT_SLOPE_DICT[heat_level]
        if not Slope.__is_work_day__(weekday):
            slope /= 2
        if Slope.__is_meal_time__(hour, minute):
            slope *= 2
        slope += Slope.__get_random__()
        if slope < 0:
            slope = 0.1
        if Slope.__is_sleep_time__(hour, minute):
            slope = 0
        return slope * (Data.MAX_VOLUME / (Data.MAX_VOLUME / 30))


class SingleGarbageCanRecordGenerator:
    TIME_START = [2019, 1, 1, 6, 30]
    TIME_END = [2019, 5, 1, 22, 30]

    def __init__(self, number):
        self.number = number
        self.id = Utils.get_garbage_can_id(number)
        self.volume_list = []
        self.time_list = []
        self.clock = datetime.datetime(
            self.TIME_START[0], self.TIME_START[1], self.TIME_START[2],
            self.TIME_START[3], self.TIME_START[4]
        )
        self.end_time = datetime.datetime(
            self.TIME_END[0], self.TIME_END[1], self.TIME_END[2],
            self.TIME_END[3], self.TIME_END[4]
        )
        self.now_volume = 0
        self.heat_level = Slope.get_heat_level(number)
        self.time_series = None

    def __is_collect_time__(self):
        hour = self.clock.hour
        minute = self.clock.minute
        for time_period in Data.RECYCLE_TIME:
            temp_hour = time_period[0]
            temp_minute = time_period[1]
            if temp_hour == hour and temp_minute == minute:
                return True
        return False

    def __is_full__(self):
        return self.now_volume >= Data.MAX_VOLUME

    def __update__(self):
        self.clock += datetime.timedelta(minutes=Data.DEFAULT_DATA_TIME_PERIOD_IN_MINUTE)
        if self.__is_collect_time__():
            self.now_volume = 0
        else:
            self.now_volume += Decimal(
                Slope.get_slope(self.heat_level, self.clock.weekday(), self.clock.hour, self.clock.minute) * Data.DEFAULT_DATA_TIME_PERIOD_IN_MINUTE,
            ).quantize(Decimal(Data.PRECISION))
        if self.__is_full__():
            self.now_volume = Data.MAX_VOLUME

    def __insert_one__(self, volume, insert_iso):
        data_dic = {
            'volume': volume,
            'garbageCan': BmobPointer('GarbageCan', self.id),
            'time': BmobDate(insert_iso)
        }
        self.volume_list.append(volume)
        self.time_list.append(insert_iso)

    def work(self):
        """
            work完成后取用：
            self.volume_list<double[]>
            self.time_list<string[]> time_iso
        """
        while self.clock <= self.end_time:
            self.__insert_one__(self.now_volume, str(self.clock))
            self.__update__()

        data_frame = pd.DataFrame({
            'time': self.time_list,
            'volume': self.volume_list
        })
        data_frame = data_frame.set_index('time')
        data_frame.index = pd.to_datetime(data_frame.index)
        self.time_series = data_frame['volume'].astype(float)

    def show_graph(self):
        print(self.id, max(self.time_series), sep=', ')
        # self.time_series.plot()
        # plt.show()


class Manager:

    def __init__(self):
        self.generator_list = []
        right = len(Data.ID_LIST)
        for garbage_can_number in range(1, right + 1):
            generator = SingleGarbageCanRecordGenerator(garbage_can_number)
            generator.work()
            self.generator_list.append(generator)

    @staticmethod
    def create_csv(time_list, volume_list, id_list):
        data = {'time': time_list, 'volume': volume_list, 'garbageCan': id_list}
        df = pd.DataFrame(data)
        df.to_csv(r'./Data.csv', columns=['time', 'volume', 'garbageCan'], index=False, sep=',')

    def work(self):
        time_list = []
        volume_list = []
        id_list = []
        for generator in self.generator_list:
            time_list.extend(generator.time_list)
            volume_list.extend(generator.volume_list)
            for i in range(len(generator.volume_list)):
                id_list.append(generator.id)
            # generator.show_graph()
        self.create_csv(time_list, volume_list, id_list)


if __name__ == '__main__':
    manager = Manager()
    manager.work()
