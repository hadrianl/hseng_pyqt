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
        self.name = name
        for k, v in kwargs.items():
            setattr(self, '_' + k, v)

class macd(indicator_base):
    def __init__(self, short=12, long=26, m=9):
        super(macd, self).__init__('MACD', short=short, long=long, m=m)

    def __str__(self):
        return f'<MACD>----SHORT:{self._short} LONG:{self._long} SIGNAL:{self._m}'

    def __call__(self, ohlc):
        self.ohlc = ohlc
        self.calc()

    def update(self, new_data):
            self.ohlc = new_data
            self.calc()

    def calc(self):
        close = self.ohlc.close
        self._diff = close.ewm(self._short).mean() - close.ewm(self._long).mean()
        self._dea = self._diff.ewm(self._m).mean()
        self._macd = (self._diff - self._dea) * 2
        self._timestamp = self.ohlc.timestamp
        self._timeindex = self.ohlc.timeindex

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


class ma(indicator_base):
    def __init__(self, **windows):
        super(ma, self).__init__('MA', **windows)
        self._windows = {('_'+k):v for k, v in windows.items()}
        # for w in self._windows:
        #     self.__dict__['ma' + str(w)] = self._close.rolling(w).mean().rename('ma'+str(w))

    def __call__(self, ohlc):
        self.ohlc = ohlc
        self.calc()

    def __str__(self):
        return f'<MA>----'+','.join(['ma' + str(w) for w in self._windows])

    def calc(self):
        self._close = self.ohlc.close
        self._timestamp = self.ohlc.timestamp
        self._timeindex = self.ohlc.timeindex
        for k, v in self._windows.items():
            self.__dict__[k] = self._close.rolling(v).mean().rename(k)

    # def update(self,newdata):
    #     for n, w in self._windows.items():
    #         new_ma = (getattr(self, n).iloc[-(w-1)]*(w-1) + newdata.close)/w
    #         self.__dict__[n]=self.__dict__[n].append(pd.Series(new_ma), ignore_index=True)

    def update(self, all_new_data):
        self.ohlc = all_new_data
        self.calc()

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def timeindex(self):
        return self._timeindex

    def to_df(self):
        return pd.concat([getattr(self, w) for w in self._windows], axis=1)

if __name__ == '__main__':
    _df = market_data('2017-12-15', '2017-12-18', 'HSIc1')
    _macd = macd(_df)
    _ma = ma(_df,10,20,30)
    print(_macd)
    print(_ma)

