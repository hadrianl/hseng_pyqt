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
import pandas as pd
from data_handle import handle_base


class indicator_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(indicator_base, self).__init__('Indicator', **kwargs)


class MACD(indicator_base):
    def __init__(self, short=12, long=26, m=9):
        super(MACD, self).__init__('MACD', short=short, long=long, m=m)

    def __str__(self):
        return f'<{self.name}>----SHORT:{self._short} LONG:{self._long} SIGNAL:{self._m}'

    def calc(self):
        self._close = self.data.close
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
        return self._macd.rename('MACD')

    @property
    def _data(self):
        return pd.concat([self.diff, self.dea, self.macd], axis=1)


class MA(indicator_base):
    def __init__(self, **windows):
        super(MA, self).__init__('MA', **windows)
        self._windows = {('_'+k): v for k, v in windows.items()}

    def __str__(self):
        return f'<{self.name}>----'+','.join(['MA' + str(w) for w in self._windows])

    def calc(self):
        for k, v in self._windows.items():
            self.__dict__[k] = self.data.close.rolling(v).mean().rename(k)

    @property
    def _data(self):
        return pd.concat([getattr(self, w) for w in self._windows], axis=1)


class STD(indicator_base):
    def __init__(self, window=60, min_periods=2):
        super(STD, self).__init__('STD', window=window, min_periods=min_periods)

    def __str__(self):
        return f'<{self.name}>----WINDOW{self._window}-MIN_PERIOUS:{self._min_periods}'

    def calc(self):
        self._inc = self.data.close - self.data.open
        self._avg = self._inc.rolling(window=self._window, min_periods=self._min_periods).mean()
        self._std = self._inc.rolling(window=self._window, min_periods=self._min_periods).std()
        self._pos_std = self._std*2
        self._neg_std = -self._std*2
        self._ratio = self._inc.abs() / self._std

    @property
    def _data(self):
        return pd.concat([self.inc, self.pos_std, self.neg_std, self.std], 1)

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

    @property
    def ratio(self):
        return self._ratio.rename('ratio')


if __name__ == '__main__':
    _df = OHLC('2017-12-15', '2017-12-18', 'HSIc1')
    _macd = MACD()
    _ma = MA(10, 20, 30)
    print(_macd)
    print(_ma)
