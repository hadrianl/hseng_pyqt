#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 16:07
# @Author  : Hadrianl 
# @File    : indicator.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
"""
该模块主要是计算指标，基于marke_data的数据
"""


from data_fetch.market_data import market_data
import pandas as pd


class indicator_base():
    def __init__(self, name, **kwargs):
        self._name = name
        for k, v in kwargs.items():
            setattr(self, '_' + k, v)

class macd(indicator_base):
    def __init__(self, marketdata, short=12, long=26, m=9):
        self._short = short
        self._long = long
        self._m = m
        self._sourcedata = marketdata.data
        # self._diff, self._dea, self._macd = MACD(self._sourcedata.close.values, self._short, self._long, self._m)
        self._diff = self._sourcedata.close.ewm(self._short).mean() - self._sourcedata.close.ewm(self._long).mean()
        self._dea = self._diff.ewm(self._m).mean()
        self._macd = (self._diff - self._dea)*2
        self._timestamp = marketdata.timestamp
        self._timeindex = marketdata.timeindex

    def __str__(self):
        return f'<MACD>----SHORT:{self._short} LONG:{self._long} SIGNAL:{self._m}'

    @property
    def diff(self):
        return self._diff.rename('diff')

    @property
    def dea(self):
        return self._dea.rename('dea')

    @property
    def macd(self):
        return self._macd.rename('macd')

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def timeindex(self):
        return self._timeindex

    def to_df(self):
        return pd.concat([self.timestamp, self.diff, self.dea, self.macd], axis=1)


class ma():
    def __init__(self,marketdata, *windows):
        self._close = marketdata.close
        self._timestamp = marketdata.timestamp
        self._timeindex = marketdata.timeindex
        self._windows = windows
        for w in self._windows:
            self.__dict__['ma' + str(w)] = self._close.rolling(w).mean().rename('ma'+str(w))

    def __str__(self):
        return f'<MA>----'+','.join(['ma' + str(w) for w in self._windows])

    def update(self,newdata):
        for w in self._windows:
            new_ma = (getattr(self, 'ma'+str(w)).iloc[-(w-1)]*(w-1) + newdata.close)/w
            self.__dict__['ma' + str(w)]=self.__dict__['ma' + str(w)].append(pd.Series(new_ma), ignore_index=True)


    @property
    def timestamp(self):
        return self._timestamp

    @property
    def timeindex(self):
        return self._timeindex

    def to_df(self):
        return pd.concat([getattr(self, 'ma' + str(w)) for w in self._windows], axis=1)

if __name__ == '__main__':
    _df = market_data('2017-12-15', '2017-12-18', 'HSIc1')
    _macd = macd(_df)
    _ma = ma(_df,10,20,30)
    print(_macd)
    print(_ma)

