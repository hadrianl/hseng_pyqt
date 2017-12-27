#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/26 0026 10:19
# @Author  : Hadrianl 
# @File    : accessory.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg

class mouseaction():
    def __init__(self, crosshair=True, info=True, axis_text=True):
        self._ch = crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self._if = info
        self.info_text = pg.TextItem(anchor=(0, 1))
        self._at = axis_text
        self.xaxis_text = pg.TextItem(anchor=(1, 1))
        self.yaxis_text = pg.TextItem()

    def __call__(self, ohlc_plt, data):
        if self._ch:
            ohlc_plt.addItem(self.vLine, ignoreBounds=True)
            ohlc_plt.addItem(self.hLine, ignoreBounds=True)
        if self._if:
            ohlc_plt.addItem(self.info_text)
        if self._at:
            ohlc_plt.addItem(self.xaxis_text)
            ohlc_plt.addItem(self.yaxis_text)


        vb = ohlc_plt.getViewBox()

        def mouseMoved(evt):
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if ohlc_plt.sceneBoundingRect().contains(pos):
                mousePoint = vb.mapSceneToView(pos)
                x_index = {0: data.timeindex.max(), 1: int(mousePoint.x()), 3: data.timeindex.min()}. \
                    get(((mousePoint.x() <= data.timeindex.min()) << 1) + (mousePoint.x() <= data.timeindex.max()))
                if self._if:
                    try:
                        text_df = data.data.iloc[x_index]
                        html = f"""
                        <span style="color:white">时间:<span/><span style="color:blue">{str(text_df.datetime)[9:16].replace(" ", "日")}<span/><br/>
                        <span style="color:white">开盘:<span/><span style="color:red">{text_df.open}<span/><br/>
                        <span style="color:white">最高:<span/><span style="color:red">{text_df.high}<span/><br/>
                        <span style="color:white">最低:<span/><span style="color:red">{text_df.low}<span/><br/>
                        <span style="color:white">收盘:<span/><span style="color:red">{text_df.close}<span/>
                        """
                        self.info_text.setPos(x_index, mousePoint.y())
                        self.info_text.setHtml(html)
                        self.xaxis_text.setText(str(text_df.datetime))
                        self.yaxis_text.setText('{:.2f}'.format(mousePoint.y()))
                    except IndexError as e:
                        print(e)

                if self._ch:
                    self.vLine.setPos(x_index)
                    self.hLine.setPos(mousePoint.y())

                if self._at:
                    self.xaxis_text.setPos(x_index, ohlc_plt.getViewBox().viewRange()[1][0])
                    self.yaxis_text.setPos(ohlc_plt.getViewBox().viewRange()[0][0], mousePoint.y())



        return pg.SignalProxy(ohlc_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)