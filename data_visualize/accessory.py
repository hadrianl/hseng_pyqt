#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/26 0026 10:19
# @Author  : Hadrianl 
# @File    : accessory.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from PyQt5 import QtCore
from data_fetch.util import MA_COLORS
class mouseaction(QtCore.QObject):
    def __init__(self, crosshair=True, info=True, axis_text=True):
        # self._veiws = parent
        self._ch = crosshair
        self.ohlc_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.ohlc_hLine = pg.InfiniteLine(angle=0, movable=False)
        self.indicator_vLine = pg.InfiniteLine(angle=90, movable=False)
        self.indicator_hLine = pg.InfiniteLine(angle=0, movable=False)
        self._if = info
        self.info_text = pg.TextItem(anchor=(0, 0))
        self._at = axis_text
        self.xaxis_text = pg.TextItem(anchor=(1, 1))
        self.yaxis_text = pg.TextItem(anchor=(1,0))

    def __call__(self, ohlc_plt, indicator_plt, market_data, ticker_data, **indicator):
        self._ohlc_plt = ohlc_plt
        self._indicator_plt = indicator_plt
        if self._ch:
            ohlc_plt.addItem(self.ohlc_vLine, ignoreBounds=True)
            ohlc_plt.addItem(self.ohlc_hLine, ignoreBounds=True)
            indicator_plt.addItem(self.indicator_vLine, ignoreBounds=True)
            indicator_plt.addItem(self.indicator_hLine, ignoreBounds=True)
        if self._if:
            ohlc_plt.addItem(self.info_text)
        if self._at:
            ohlc_plt.addItem(self.xaxis_text)
            ohlc_plt.addItem(self.yaxis_text)
        if 'i_ma' in indicator:
            self._i_ma = indicator['i_ma']
            self.ma_text = pg.TextItem(anchor=(1, 0))
            ohlc_plt.addItem(self.ma_text)
        if 'i_macd' in indicator:
            self._i_macd = indicator['i_macd']
            self.macd_text = pg.TextItem(anchor=(0, 0))
            indicator_plt.addItem(self.macd_text)


        ohlc_vb = ohlc_plt.getViewBox()
        indicator_vb = indicator_plt.getViewBox()
        def mouseMoved(evt):
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if ohlc_plt.sceneBoundingRect().contains(pos) or indicator_plt.sceneBoundingRect().contains(pos):
                mousePoint = ohlc_vb.mapSceneToView(pos) if ohlc_plt.sceneBoundingRect().contains(pos) else indicator_vb.mapSceneToView(pos)
                t_max = market_data.timeindex.max()
                t_min = market_data.timeindex.min()
                x_type = ((mousePoint.x() <= t_min - 3) << 1) + (mousePoint.x() <= t_max + 3)
                x_index = {0: t_max + 3 , 1: int(mousePoint.x()), 3: t_min -3 }.get(x_type)
                self.x_index = x_index
                if self._if:
                    try:
                        if x_index == t_max + 1:
                            text_df = ticker_data.data.iloc[0]
                        else:
                            text_df = market_data.data.iloc[x_index]
                        html = f"""
                        <span style="color:white;font-size:16px">时间:<span/><span style="color:blue">{str(text_df.datetime)[8:16].replace(" ", "日")}<span/><br/>
                        <span style="color:white;font-size:16px">开盘:<span/><span style="color:red">{text_df.open}<span/><br/>
                        <span style="color:white;font-size:16px">最高:<span/><span style="color:red">{text_df.high}<span/><br/>
                        <span style="color:white;font-size:16px">最低:<span/><span style="color:red">{text_df.low}<span/><br/>
                        <span style="color:white;font-size:16px">收盘:<span/><span style="color:red">{text_df.close}<span/>
                        """
                        self.info_text.setPos(ohlc_vb.viewRange()[0][0],ohlc_vb.viewRange()[1][1])
                        # self.info_text.setPos(0, 0)
                        self.info_text.setHtml(html)
                        self.xaxis_text.setText(str(text_df.datetime))
                        self.yaxis_text.setText('{:.2f}'.format(mousePoint.y()))
                    except IndexError as e:
                        # print(e)
                        pass
                if self._ch:
                    self.ohlc_vLine.setPos(x_index)
                    self.ohlc_hLine.setPos(mousePoint.y())
                    self.indicator_vLine.setPos(x_index)
                    self.indicator_hLine.setPos(mousePoint.y())

                if self._at:
                    self.xaxis_text.setPos(x_index, ohlc_plt.getViewBox().viewRange()[1][0])
                    self.yaxis_text.setPos(ohlc_plt.getViewBox().viewRange()[0][1], mousePoint.y())

                if 'i_ma' in indicator:
                    try:
                        ma_text = [f'<span style="color:rgb{MA_COLORS[k]}">MA{k[-2:]}:{round(getattr(self._i_ma, k)[x_index],2)}<span/>' for k, v in self._i_ma._windows.items()]
                        self.ma_text.setHtml('  '.join(ma_text))
                        self.ma_text.setPos(ohlc_vb.viewRange()[0][1],ohlc_vb.viewRange()[1][1])
                    except Exception as e:
                        pass

                if 'i_macd' in indicator:
                    try:
                        macd_text = f'<span style="color:red">MACD:{round(indicator["i_macd"].Macd[x_index], 2)}<span/>  ' \
                                    f'<span style="color:yellow">DIFF:{round(indicator["i_macd"].diff[x_index], 2)}<span/>  ' \
                                    f'<span style="color:white">DEA:{round(indicator["i_macd"].dea[x_index], 2)}<span/>  '
                        self.macd_text.setHtml(macd_text)
                        self.macd_text.setPos(indicator_vb.viewRange()[0][0], indicator_vb.viewRange()[1][1])
                    except Exception as e:
                        pass



        return pg.SignalProxy(ohlc_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)