# coding=utf-8
import pandas as pd

from analyzer import Analyzer
from bmob import *
from bmob_beans import *
from generator.database import query_data

bmob = Bmob("cc9b6713ae4044193269990fede0c4f3", "1728823c0ecc355d0898ea9e836b03ce")


class Utils:
    @staticmethod
    def parse_iso_time_to_epoch(iso):
        str_list = iso.replace('-', ':').replace(' ', ':').split(':')
        year = int(str_list[0])
        month = int(str_list[1])
        day = int(str_list[2])
        hour = int(str_list[3])
        minute = int(str_list[4])
        second = int(str_list[5])
        return time.mktime((year, month, day, hour, minute, second, 0, 0, 0))


class GarbageCanRepository:
    def __init__(self, garbage_can):
        self.garbage_can = garbage_can
        self.time_list, self.volume_list = self.__get_garbage_record_list_local__()
        self.garbage_record_time_series = self.__get_time_series__()

    def __get_garbage_record_list_local__(self):
        print('Getting all garbage record of GarbageCan[%s]...' % self.garbage_can.object_id)
        garbage_record_time_arr = []
        garbage_record_volume_arr = []

        garbage_record_item_list = query_data(self.garbage_can.object_id)
        for tuple_item in garbage_record_item_list:
            dict_item = {
                'objectId': '',
                'garbageCan': {
                    'objectId': tuple_item[1]
                },
                'volume': tuple_item[2],
                'time': tuple_item[3]
            }
            garbage_record_item = GarbageRecord(dict_item)
            garbage_record_time_arr.append(garbage_record_item.time)
            garbage_record_volume_arr.append(garbage_record_item.volume)
        return garbage_record_time_arr, garbage_record_volume_arr

    def __get_time_series__(self):
        data_frame = pd.DataFrame({
            'time': self.time_list,
            'volume': self.volume_list
        })
        data_frame = data_frame.set_index('time')
        data_frame.index = pd.to_datetime(data_frame.index)
        return data_frame['volume'].astype(float)


class RecyclerPlaceRepository:
    def __init__(self, recycler_place):
        self.recycler_place = recycler_place
        self.garbage_can_list = self.__get_garbage_can_list__()
        self.garbage_can_repository_list = []
        for garbage_can in self.garbage_can_list:
            self.garbage_can_repository_list.append(GarbageCanRepository(garbage_can))

    def __get_garbage_can_list__(self):
        print('Getting all garbage cans in RecyclerPlace[%s], areaCode=[%s], blockCode=[%s]...' %
              (self.recycler_place.object_id, self.recycler_place.area_code, self.recycler_place.area_code)
              )
        garbage_can_list = []
        garbage_can_item_list = bmob.find('GarbageCan',
                                          BmobQuerier()
                                          .addWhereEqualTo('areaCode', self.recycler_place.area_code)
                                          .addWhereEqualTo('blockCode', self.recycler_place.block_code)
                                          ).jsonData.get(u'results')
        for garbage_can_item_json in garbage_can_item_list:
            garbage_can_item = GarbageCan(garbage_can_item_json)
            garbage_can_list.append(garbage_can_item)
        return garbage_can_list


class UserRepository:
    def __init__(self, user_id):
        self.user_id = user_id
        self.recycler_place_list = self.__get_recycler_place__()
        self.recycler_place_repository_list = []
        for recycler_place in self.recycler_place_list:
            self.recycler_place_repository_list.append(RecyclerPlaceRepository(recycler_place))

    def __get_recycler_place__(self):
        print('Getting user[%s]\'s all recycler place...' % self.user_id)
        recycler_place_list = []
        recycler_place_item_list = bmob.find('RecyclerPlace',
                                             BmobQuerier().addWhereEqualTo('recycler', self.user_id)
                                             ).jsonData.get('results')
        for recycler_place_item_json in recycler_place_item_list:
            recycler_place_item = RecyclerPlace(recycler_place_item_json)
            recycler_place_list.append(recycler_place_item)
        return recycler_place_list


class Worker:

    def __init__(self):
        self.user_id_list = self.__get_all_user_id_list__()
        self.manager_dic = {}

    @staticmethod
    def __get_all_user_id_list__():
        print('Getting all user id...')
        all_user_id_list = []
        all_user_list = bmob.find('_User').jsonData.get('results')
        for user_json in all_user_list:
            user = FRUser(user_json)
            all_user_id_list.append(user.object_id)
        return all_user_id_list

    def __get_data_manager__(self, user_id):
        manager = self.manager_dic.get(user_id)
        if manager is not None:
            return manager
        manager = UserRepository(user_id)
        self.manager_dic[user_id] = manager
        return manager


if __name__ == '__main__':
    user_id = 'Rnz0GGGL'

    worker = Worker()
    result_dic = {}
    for recycler_place_repository in worker.__get_data_manager__(user_id).recycler_place_repository_list:
        for garbage_can_repository in recycler_place_repository.garbage_can_repository_list:
            manager = garbage_can_repository

            print("Working on garbage can [%s].." % manager.garbage_can.object_id)
            data = Analyzer(manager, show_plot=False)
            data.predict()
            result_dic[manager.garbage_can.object_id] = data.predict_recycle_time_list
            print("Done garbage can [%s]!" % manager.garbage_can.object_id)
    print(result_dic)

