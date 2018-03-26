#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 16:07
# @Author  : Hadrianl 
# @File    : indicator.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
"""
该模块主要是计算指标，基于marke_data的数据
"""


from data_fetch.market_data import OHLC
from util import H_logger
import pandas as pd
from data_handle import handle_base


class indicator_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(indicator_base, self).__init__('Indicator', **kwargs)

class Macd(indicator_base):
    def __init__(self, short=12, long=26, m=9):
        super(Macd, self).__init__('MACD', short=short, long=long, m=m)

    def __str__(self):
        return f'<{self.name}>----SHORT:{self._short} LONG:{self._long} SIGNAL:{self._m}'

    def calc(self):
        self._close = self.ohlc.close
        self._diff = self._close.ewm(self._short).mean() - self._close.ewm(self._long).mean()
        self._dea = self._diff.ewm(self._m).mean()
        self._macd = (self._diff - self._dea) * 2

    @property
    def diff(self):
        return self._diff.rename('diff')

    @property
    def dea(self):
        return self._dea.rename('dea')

    @property
    def macd(self):
        return self._macd.rename('Macd')

    def to_df(self):
        return pd.concat([self.timestamp, self.diff, self.dea, self.macd], axis=1)


class Ma(indicator_base):
    def __init__(self, **windows):
        super(Ma, self).__init__('MA', **windows)
        self._windows = {('_'+k): v for k, v in windows.items()}

    def __str__(self):
        return f'<{self.name}>----'+','.join(['Ma' + str(w) for w in self._windows])

    def calc(self):
        for k, v in self._windows.items():
            self.__dict__[k] = self.ohlc.close.rolling(v).mean().rename(k)

    def to_df(self):
        return pd.concat([getattr(self, w) for w in self._windows], axis=1)


class Std(indicator_base):
    def __init__(self, window=60, min_periods=2):
        super(Std, self).__init__('STD', window=window, min_periods=min_periods)

    def __str__(self):
        return f'<{self.name}>----WINDOW{self._window}-MIN_PERIOUS:{self._min_periods}'

    def calc(self):
        self._inc = self.ohlc.close - self.ohlc.open
        self._avg = self._inc.rolling(window=self._window, min_periods=self._min_periods).mean()
        self._std = self._inc.rolling(window=self._window, min_periods=self._min_periods).std()
        self._pos_std = self._std*2
        self._neg_std = -self._std*2

    @property
    def inc(self):
        return self._inc.rename('inc')

    @property
    def pos_std(self):
        return self._pos_std.rename('pos_std')

    @property
    def neg_std(self):
        return self._neg_std.rename('neg_std')

    @property
    def std(self):
        return self._std.rename('std')


if __name__ == '__main__':
    _df = OHLC('2017-12-15', '2017-12-18', 'HSIc1')
    _macd = Macd(_df)
    _ma = Ma(_df, 10, 20, 30)
    print(_macd)
    print(_ma)
