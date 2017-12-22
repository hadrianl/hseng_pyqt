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
        self._sql = f"select datetime, open, high, low, close from stock_data.index_min \
                                    where datetime>=\"{start}\" \
                                    and datetime<\"{end} \"\
                                    and code=\"{symbol}\""
        self.data = pd.read_sql(self._sql, self._conn)
        self.indicators = {}

    def __str__(self):
        return f"<{self.ktype}-{self.symbol}> *{self.data['datetime'].min()}-->{self.data['datetime'].max()}*"

    def __repr__(self):
        return self.data.__repr__()

    def indicator_register(self,indicator):
            self.indicators[indicator.name] = indicator(self)

    def update(self, newdata):
        self.data = self.data.append(newdata.data, ignore_index=True)
        for i,v in self.indicators.items():
            v.update(self)

class new_market_data(market_data_base):
    def __init__(self,old_market_data):
        super(new_market_data, self).__init__()
        self.symbol = old_market_data.symbol
        self.last_time = old_market_data.data.datetime.iloc[-1]
        for i in range(60):
            self.last_time += timedelta(minutes=1)
            self._sql = f'select datetime, open, high, low, close from stock_data.index_min where datetime=\"{str(self.last_time)}\" and code=\"{self.symbol}\" '
            # print(self._sql)
            # print(self.symbol)
            # print(self.last_time)
            self.data = pd.read_sql(self._sql, self._conn)
            if not self.data.empty:
                break

if __name__ == '__main__':
    df = market_data('2017-12-15','2017-12-18','HSIc1')
    print(df)
    print(df.__repr__())