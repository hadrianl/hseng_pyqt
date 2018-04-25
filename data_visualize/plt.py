#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/16 0016 12:01
# @Author  : Hadrianl 
# @File    : plt.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_visualize.baseitems import plt_base

class MainPlt(plt_base):
    def __init__(self, name, date_xaxis):
        super(MainPlt, self).__init__(name, date_xaxis)
        self.setMinimumHeight(300)


class IndicatorPlt(plt_base):
    def __init__(self, name, date_xaxis, height_range=None):
        super(IndicatorPlt, self).__init__(name, date_xaxis)
        if height_range:
            self.setMaximumHeight(height_range[0])
            self.setMinimumHeight(height_range[1])
        self.hideAxis('bottom')

class SlicerPlt(plt_base):
    def __init__(self, name, date_xaxis):
        super(SlicerPlt, self).__init__(name, date_xaxis)
        self.hideAxis('right')
        self.setMaximumHeight(80)
        self.setMouseEnabled(False, False)
