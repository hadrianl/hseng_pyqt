#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/22 0022 14:46
# @Author  : Hadrianl 
# @File    : spec_handler.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_handle import handle_base
import pandas as pd
import datetime as dt
class spec_handler_base(handle_base):
    def __init__(self, name, **kwargs):
        self.name = name
        super(spec_handler_base, self).__init__('spec_handler', **kwargs)


class MACD_HL_MARK(spec_handler_base):
    def __init__(self):
        super(MACD_HL_MARK, self).__init__('MACD_HL_MARK')

    def calc(self):
        self.macd = self.ohlc.extra_data['MACD']
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
    def _data(self):
        return {'high_pos': self.high_pos, 'low_pos': self.low_pos}

    @property
    def high_pos(self):
        return self._high_pos

    @property
    def low_pos(self):
        return self._low_pos

class BuySell(spec_handler_base):
    def __init__(self, windows=15, real_bar_rate=0.6, overlap_rate=0.4):
        assert windows>=2
        super(BuySell, self).__init__('BuySell', windows=windows, real_bar_rate=real_bar_rate, overlap_rate=overlap_rate)

    def calc(self):
        ohlc_data = self.ohlc.data
        i_std = self.ohlc.extra_data['STD']
        real_bar_rate = self._real_bar_rate
        overlap_rate = self._overlap_rate
        w = self._windows
        self.ohlc_std = pd.concat([ohlc_data, i_std.std,
                                   (i_std.inc.abs() > i_std.std * 1.5).rename('b_gt_std'),
                                   ((ohlc_data.close - ohlc_data.open).abs() >= (ohlc_data.high - ohlc_data.low).abs()*real_bar_rate).rename('b_real_bar')], 1)
        self.data_merged = pd.concat([self.ohlc_std.shift(n) for n in range(0, -w, -1)], 1, keys=[n for n in range(1, w + 1)], names=['shift_','data_type'])

        def buysell(row):
            unstack = row.unstack()
            Open = unstack.open
            Close = unstack.close
            o1 = Open.iloc[0]
            c1 = Close.iloc[0]
            b_s = c1 > o1
            if b_s:
                cond1 = (Open > o1).rename('cond1')
                cond2 = (Close > c1).rename('cond2')
                cond3 = (c1 > Open).rename('cond3')
                cond4 = (((c1 - Open) > (Close - o1) * overlap_rate)).rename('cond4')
                cond = cond1 & cond2 & cond3 & cond4 & unstack.b_gt_std & unstack.b_real_bar
            else:
                cond1 = (Open < o1).rename('cond1')
                cond2 = (Close < c1).rename('cond2')
                cond3 = (c1 < Open).rename('cond3')
                cond4 = ((( Open - c1) > (o1 - Close ) * overlap_rate)).rename('cond4')
                cond = cond1 & cond2 & cond3 & cond4 & unstack.b_gt_std & unstack.b_real_bar
            unstack = unstack[cond].assign(bs=['S', 'B'][b_s])
            return  unstack['bs']

        self._bs = self.data_merged.apply(buysell, 1).dropna(how='all').stack()._set_name('bs')

    @property
    def _data(self):
        return self._bs

    @property
    def bs_points(self):
        bs = self._bs.reset_index().apply(lambda x: (x.datetime + dt.timedelta(minutes=int(x.shift_)),
                                                     0,
                                                     x.bs
                                                     ), 1).drop('shift_', 1).set_index('datetime').loc[:,'bs']
        return bs

    @property
    def buy_points(self):
        bs = self.bs_points
        return bs[bs=='B']

    @property
    def sell_points(self):
        bs = self.bs_points
        return bs[bs=='S']