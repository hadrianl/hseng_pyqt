#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/22 0022 14:46
# @Author  : Hadrianl 
# @File    : spec_handler.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_handle import handle_base
import pandas as pd
class spec_handler_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(spec_handler_base, self).__init__('spec_handler', **kwargs)


class MACD_HL_MARK(spec_handler_base):
    def __init__(self):
        super(MACD_HL_MARK, self).__init__('macd_hl_mark')

    def calc(self):
        self.macd = self.ohlc.indicators['MACD']
        self.macd_gt_zero = self.macd.macd > 0
        self.macd_area_num = self.create_area(self.macd_gt_zero).rename('macd_area')
        self.area_close_frame = pd.concat([self.macd_area_num, self.macd.ohlc.high, self.macd.ohlc.low], 1).reset_index()
        data_pos=self.area_close_frame.groupby('macd_area').apply(lambda x: [x.loc[x.high.idxmax(), ['high', 'datetime']], x.loc[x.low.idxmin(), ['low', 'datetime']]])
        self._high_pos = pd.Series(data_pos.str[0].str[0].values, index=data_pos.str[0].str[1])._set_name('high')
        self._low_pos = pd.Series( data_pos.str[1].str[0].values, index=data_pos.str[1].str[1])._set_name('low')

    def create_area(self, v):
        k = v.copy()
        k.iloc[0] = 1
        for i in range(1,len(v)):
            if v.iloc[i] != v.iloc[i-1]:
                k.iloc[i] = k.iloc[i-1] + 1
            else:
                k.iloc[i] = k.iloc[i - 1]
        return k

    @property
    def high_pos(self):
        return self._high_pos

    @property
    def low_pos(self):
        return self._low_pos