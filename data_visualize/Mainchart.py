#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/21 0021 11:49
# @Author  : Hadrianl 
# @File    : Mainchart.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from data_visualize.baseitems import DateAxis, CandlestickItem
from data_handle.indicator import ma

class mainchart(pg.PlotItem):
    """
    主图表
    """
    def __init__(self, data=None, title='K线图', labels={'top': '恒指期货'},
                 name='mianchart', axisItems={'bottom':DateAxis}, *args):
        super(mainchart, self).__init__(title=title, labels=labels,  axisItems=axisItems, *args)
        self._data = data
        self._ohlcitems = CandlestickItem()
        self._ohlcitems.set_data(data)
        self.addItem(self._ohlcitems)
        self.showGrid(x=True, y=True)

    def addIndicator(self, indicator):
        for k in indicator:
            if k == 'ma':
                i_ma = ma(data, *indicator[k])
                for w in i_ma._windows:  ##在主图表画出均线
                    ohlc_plt.plot(data.timeindex, getattr(i_ma, 'ma' + str(w)),
                                  pen=pg.mkPen(color=MA_COLORS.get('ma' + str(w), 'w'), width=1))
