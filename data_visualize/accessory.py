#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/26 0026 10:19
# @Author  : Hadrianl 
# @File    : accessory.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from PyQt5 import QtCore
from util import MA_COLORS


class mouseaction(QtCore.QObject):
    def __init__(self, crosshair=True, info=True, axis_text=True):
        self._ch = crosshair
        self._if = info
        self._at = axis_text
        self.xaxis_text = pg.TextItem(anchor=(1, 1))
        self.yaxis_text = pg.TextItem(anchor=(1, 0))
        self.cross_hair_pen = pg.mkPen(color='y', dash=[3, 4])

    def __call__(self, main_plt, indicator_plt, indicator2_plt, date_slicer_plt, market_data, graphs):
        self._main_plt = main_plt
        self._indicator_plt = indicator_plt
        if self._ch:
            main_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            main_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator2_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator2_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            date_slicer_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline'), ignoreBounds=True)
            date_slicer_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline'), ignoreBounds=True)
        if self._at:
            main_plt.addItem(self.xaxis_text)
            main_plt.addItem(self.yaxis_text)

        plt_list = [main_plt, indicator_plt, indicator2_plt, date_slicer_plt]

        def mouseMoved(evt):
            pos = evt[0]  # using signal proxy turns original arguments into a tuple
            # if ohlc_plt.sceneBoundingRect().contains(pos) or indicator_plt.sceneBoundingRect().contains(pos):
            #     mousePoint = ohlc_vb.mapSceneToView(pos) if ohlc_plt.sceneBoundingRect().contains(pos) else indicator_vb.mapSceneToView(pos)
            # if ohlc_plt.parentItem().sceneBoundingRect().contains(pos):
            inside = False
            for plt in plt_list:
                if plt.sceneBoundingRect().contains(pos):
                    inside = True
                    self.mousePoint = mousePoint = plt.vb.mapSceneToView(pos)
                    t_max = market_data.x.max()
                    t_min = market_data.x.min()
                    x_type = ((mousePoint.x() <= t_min - 3) << 1) + (mousePoint.x() <= t_max + 3)
                    x_index = {0: t_max + 3, 1: int(mousePoint.x()), 3: t_min - 3}.get(x_type)
                    break
                else:
                    x_index = market_data.x.max()

            for plt in plt_list:
                if self._ch:
                    for i in plt.items:
                        if isinstance(i, pg.InfiniteLine) and i.name() == 'hline':
                            if plt.sceneBoundingRect().contains(pos):
                                i.setPos(mousePoint.y())
                                i.show()
                            else:
                                i.hide()
                        if isinstance(i, pg.InfiniteLine) and i.name() == 'vline':
                            i.setPos(x_index)

                if self._if:
                    try:
                        text_df = market_data.data.iloc[x_index]
                        self.xaxis_text.setText(str(text_df.name))
                        self.yaxis_text.setText('{:.2f}'.format(mousePoint.y())) if inside else ...
                    except IndexError:
                        pass

                    for k, v in graphs.items():
                        text_func = getattr(v, 'set_info_text', None)
                        if text_func:
                            text_func(x_index)

                if self._at:
                    self.xaxis_text.setPos(x_index, main_plt.vb.viewRange()[1][0])
                    self.yaxis_text.setPos(main_plt.vb.viewRange()[0][1], mousePoint.y()) if inside else ...


        return pg.SignalProxy(main_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
