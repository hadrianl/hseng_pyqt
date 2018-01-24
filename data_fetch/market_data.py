#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:28
# @Author  : Hadrianl 
# @File    : market_data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()
import sqlalchemy
from data_fetch.util import *
from numpy.random import choice
from datetime import timedelta


class market_data_base():
    def __init__(self):
        self._conn = sqlalchemy.create_engine(
            f'mysql+pymysql://{KAIRUI_MYSQL_USER}:{KAIRUI_MYSQL_PASSWD}@{KAIRUI_SERVER_IP}')
        self.data = pd.DataFrame()

    @property
    def open(self):
        return self.data['open']

    @property
    def high(self):
        return self.data['high']

    @property
    def low(self):
        return self.data['low']

    @property
    def close(self):
        return self.data['close']

    @property
    def datetime(self):
        return  self.data['datetime']

    @property
    def timestamp(self):
        return self.data['datetime'].apply(lambda x: x.timestamp()).rename('timestamp')

    @property
    def timeindex(self):
        return self.timestamp.index.to_series()



class market_data(market_data_base):
    def __init__(self, start, end,  symbol, ktype='1M'):
        super(market_data, self).__init__()
        self.start = start
        self.end = end
        self.ktype = ktype
        self.symbol = symbol
        self._sql = f"select datetime, open, high, low, close from carry_investment.futures_min \
                                    where datetime>=\"{start}\" \
                                    and datetime<\"{end} \"\
                                    and prodcode=\"{symbol}\""
        self.data = pd.read_sql(self._sql, self._conn)
        self.data.datetime = pd.to_datetime(self.data.datetime)
        self.indicators = {}
        self.bar_size = 200

    def __str__(self):
        return f"<{self.ktype}-{self.symbol}> *{self.data['datetime'].min()}-->{self.data['datetime'].max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def indicator_register(self,indicator):
            self.indicators[indicator.name] = indicator(self)

    def update(self, tick_data):
        new_ohlc = tick_data._ohlc_queue.get_nowait()
        self.data = self.data.append(new_ohlc, ignore_index=True)
        if len(self.data) > self.bar_size:
            self.data.drop(self.data.index[0],inplace=True)
        for i,v in self.indicators.items():
            v.update(self)

    def resample(self, ktype):
        self.data_resampled =  self.data.resample(ktype, on='datetime').agg({'open':lambda x:x.head(1),'high':lambda x:x.max(),'low':lambda x:x.min(), 'close':lambda x:x.tail(1)})
        return self.data_resampled
# class new_market_data(market_data_base):
#     def __init__(self,old_market_data):
#         super(new_market_data, self).__init__()
#         self.symbol = old_market_data.symbol
#         self.last_time = old_market_data.data.datetime.iloc[-1]
#         for i in range(60):
#             self.last_time += timedelta(minutes=1)
#             self._sql = f'select datetime, open, high, low, close from stock_data.index_min where datetime=\"{str(self.last_time)}\" and code=\"{self.symbol}\" '
#             # print(self._sql)
#             # print(self.symbol)
#             # print(self.last_time)
#             self.data = pd.read_sql(self._sql, self._conn)
#             if not self.data.empty:
#                 break

if __name__ == '__main__':
    df = market_data('2018-01-18', '2018-01-19 11:00:00', 'HSIF8')
    print(df)
    print(df.__repr__())