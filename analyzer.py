import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot

import utils
from const import RECYCLE_TIME


class Data:
    def __init__(self, garbage_record_manager):
        self.data_manager = garbage_record_manager
        self.time_series = self.data_manager.garbage_record_time_series
        df = pd.DataFrame({
            'ds': self.data_manager.time_list,
            'y': self.data_manager.volume_list
        })
        df['ds'] = pd.to_datetime(df['ds'])
        self.prophet_data_frame = df
        self.predict_time_list = None
        self.predict_value_list = None
        self.predict_time_series = None

    def predict(self):
        m = Prophet(n_changepoints=0, daily_seasonality=10)
        m.fit(self.prophet_data_frame)
        frequency_in_minute = 1
        day = 1
        periods = 24 * (60 // frequency_in_minute) * day
        future = m.make_future_dataframe(periods=1440, freq='min')
        forecast = m.predict(future)
        fig = m.plot(forecast)
        plt.show()
        self.predict_value_list = forecast['yhat'].values[-periods:]
        self.predict_time_list = forecast['ds'].values[-periods:]

        data_frame = pd.DataFrame({
            'ds': self.predict_time_list,
            'y': self.predict_value_list
        })
        data_frame = data_frame.set_index('ds')
        data_frame.index = pd.to_datetime(data_frame.index)
        self.predict_time_series = data_frame['y'].astype(float)

    def shift(self):
        ds = self.predict_time_list
        y = self.predict_value_list
        # 截取7：30-20：30
        today = utils.convert_datetime64_to_datatime(ds[0]).date()
        start_time = datetime.datetime(today.year, today.month, today.day,
                                       RECYCLE_TIME[0][0], RECYCLE_TIME[0][1])
        end_time = datetime.datetime(today.year, today.month, today.day,
                                     RECYCLE_TIME[len(RECYCLE_TIME) - 1][0], RECYCLE_TIME[len(RECYCLE_TIME) - 1][1])
        for i in range(len(ds)):
            time = utils.convert_datetime64_to_datatime(ds[i])
            if not (start_time <= time <= end_time):
                y[i] = 0
        self.build_time_series(ds, y).plot()
        plt.show()
        # 去除上下限外的值
        upper_limit = self.data_manager.garbage_can.max_volume
        lower_limit = 0
        limit_series = pd.Series(y)
        y = self.__cut_series__(limit_series.values, lower_limit, upper_limit)
        self.build_time_series(ds, y).plot()
        plt.show()
        # 计算差分
        diff_y = pd.Series(y).diff()
        # 截取上升段落
        go_up_periods = self.__cut_series__(diff_y.values, 0, None, False)
        for i in range(len(go_up_periods)):
            if np.isnan(go_up_periods[i]):
                y[i] = 0
        self.build_time_series(ds, y).plot()
        plt.show()
        # 相似平移：获取上升片段
        go_up_period_data = []
        i = 0
        while i < len(y):
            if y[i] != 0:
                ds_list = []
                y_list = []
                while y[i] == 0:
                    ds_list.append(ds[i])
                    y_list.append(y[i])
                    i += 1
                dict_record = {
                    'ds': ds_list,
                    'y': y_list
                }
                go_up_period_data.append(dict_record)
            i += 1
        # 相似平移：对上升片段作局部线性回归
        # for
        self.build_time_series(ds, y).plot()
        plt.show()

    @staticmethod
    def __cut_series__(y, lower_limit=None, higher_limit=None, clear_nan=True):
        temp_series = pd.Series(y)
        if lower_limit is not None:
            temp_list = temp_series.where(temp_series >= lower_limit)
            if clear_nan:
                for i in range(len(temp_list)):
                    if np.isnan(temp_list[i]):
                        temp_list[i] = lower_limit
        if higher_limit is not None:
            temp_list = temp_series.where(temp_series <= higher_limit)
            if clear_nan:
                for i in range(len(temp_list)):
                    if np.isnan(temp_list[i]):
                        temp_list[i] = higher_limit
        return temp_list

    @staticmethod
    def build_time_series(ds, y):
        data_frame = pd.DataFrame({
            'ds': ds,
            'y': y
        })
        data_frame = data_frame.set_index('ds')
        data_frame.index = pd.to_datetime(data_frame.index)
        return data_frame['y'].astype(float)
