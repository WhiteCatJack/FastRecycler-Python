from decimal import Decimal

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bmob import *
from const import *

b = Bmob("cc9b6713ae4044193269990fede0c4f3", "1728823c0ecc355d0898ea9e836b03ce")


class Utils:
    @staticmethod
    def get_garbage_can_id(number):
        return ID_LIST[number - 1]

    @staticmethod
    def get_formatted_time(year, month, day, hour, minute):
        return str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + \
               str(hour).zfill(2) + ':' + str(minute).zfill(2) + ':00'

    @staticmethod
    def random_0_1():
        return np.random.random()


class Slope:
    HEAT_SLOPE_DICT = {
        HEAT_3: 9,
        HEAT_2: 3,
        HEAT_1: 1
    }

    @staticmethod
    def get_heat_level(number):
        if number in HOT_3_LIST:
            return HEAT_3
        elif number in HOT_2_LIST:
            return HEAT_2
        else:
            return HEAT_1

    @staticmethod
    def __is_work_day__(weekday):
        return 0 <= weekday <= 4

    @staticmethod
    def __judge_time_in_period(hour, minute, period_list):
        for time_period in period_list:
            left = datetime.time(hour=time_period[0][0], minute=time_period[0][1])
            right = datetime.time(hour=time_period[1][0], minute=time_period[1][1])
            now = datetime.time(hour=hour, minute=minute)
            if left <= now <= right:
                return True
        return False

    @staticmethod
    def __is_meal_time__(hour, minute):
        return Slope.__judge_time_in_period(hour, minute, MEAL_TIME_PERIOD)

    @staticmethod
    def __is_sleep_time__(hour, minute):
        return Slope.__judge_time_in_period(hour, minute, SLEEP_TIME_PERIOD)

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
        return slope * (MAX_VOLUME / (MAX_VOLUME / 30))


class SingleGarbageCanRecordGenerator:

    def __init__(self, number):
        self.number = number
        self.id = Utils.get_garbage_can_id(number)
        self.volume_list = []
        self.time_list = []
        self.clock = datetime.datetime(
            TIME_START[0], TIME_START[1], TIME_START[2],
            TIME_START[3], TIME_START[4]
        )
        self.end_time = datetime.datetime(
            TIME_END[0], TIME_END[1], TIME_END[2],
            TIME_END[3], TIME_END[4]
        )
        self.now_volume = 0
        self.heat_level = Slope.get_heat_level(number)
        self.time_series = None

    def __is_collect_time__(self):
        hour = self.clock.hour
        minute = self.clock.minute
        for time_period in RECYCLE_TIME:
            temp_hour = time_period[0]
            temp_minute = time_period[1]
            if temp_hour == hour and temp_minute == minute:
                return True
        return False

    def __is_full__(self):
        return self.now_volume >= MAX_VOLUME

    def __update__(self):
        self.clock += datetime.timedelta(minutes=DEFAULT_DATA_TIME_PERIOD_IN_MINUTE)
        if self.__is_collect_time__():
            self.now_volume = 0
        else:
            slope = Slope.get_slope(self.heat_level, self.clock.weekday(), self.clock.hour, self.clock.minute)
            self.now_volume += Decimal(
                slope * DEFAULT_DATA_TIME_PERIOD_IN_MINUTE,
            ).quantize(Decimal(PRECISION))
        if self.__is_full__():
            self.now_volume = MAX_VOLUME

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
        self.time_series.plot()
        plt.show()


class Manager:

    def __init__(self):
        self.generator_list = []
        right = len(ID_LIST)
        for garbage_can_number in range(1, right + 1):
            generator = SingleGarbageCanRecordGenerator(garbage_can_number)
            generator.work()
            self.generator_list.append(generator)

    @staticmethod
    def create_csv(time_list, volume_list, id_list):
        data = {'time': time_list, 'volume': volume_list, 'garbageCan': id_list}
        df = pd.DataFrame(data)
        df.to_csv(r'../Data.csv', columns=['time', 'volume', 'garbageCan'], index=False, sep=',')

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
