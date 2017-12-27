#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/27 0027 14:45
# @Author  : Hadrianl 
# @File    : tickdata.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data_base
import pandas as pd
class tickdatas(market_data_base):
    def __init__(self, symbol):
        self._symbol = symbol
        self._timestamp_range = None
        self._done = False
        self.datalist = []
        self._data = pd.DataFrame(columns=['datetime', 'tick', 'vol'])

    def append(self,tick):
        self.datalist.append(tick)
        self._data.append(tick)

    @property
    def data(self):
        d = {'datetime': self._data.datetime,
             'open': self._data.tick[0],
             'high': self._data.tick.max(),
             'low': self._data.tick.min(),
             'close': self._data.tick[-1]}
        return pd.DataFrame(d)



