#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/27 0027 14:45
# @Author  : Hadrianl 
# @File    : tickdata.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data_base
import pandas as pd
from datetime import datetime
class tickdatas(market_data_base):
    def __init__(self, symbol, timeindex):
        self._symbol = symbol
        self._timeindex = timeindex
        self._done = False
        self._data = pd.DataFrame(columns=['datetime', 'tick', 'vol'])

    def append(self,tick):
        if not self._data.empty:
            if (tick['datetime'].timestamp()//60)*60 == self._timestamp:
                self._data = self._data.append(tick, ignore_index=True)
            else:
                raise Exception('数据不在同一分钟内')
        else:
            self._data = self._data.append(tick, ignore_index=True)
            self._timestamp = (self._data.datetime[0].timestamp()//60)*60
            print(self._timestamp)


    @property
    def data(self):
        d = {'datetime': datetime.fromtimestamp(self._timestamp),
             'open': self._data.tick.iloc[0],
             'high': self._data.tick.max(),
             'low': self._data.tick.min(),
             'close': self._data.tick.iloc[-1]}
        return pd.DataFrame(d, index=[self._timeindex], columns=['datetime', 'open', 'high', 'low', 'close'])





