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
        self.info_text = pg.TextItem(anchor=(0, 0))
        self._at = axis_text
        self.xaxis_text = pg.TextItem(anchor=(1, 1))
        self.yaxis_text = pg.TextItem(anchor=(1, 0))
        self.cross_hair_pen = pg.mkPen(color='y', dash=[3, 4])

    def __call__(self, ohlc_plt, indicator_plt, std_plt, date_slicer, market_data, **indicator):
        self._ohlc_plt = ohlc_plt
        self._indicator_plt = indicator_plt
        if self._ch:
            ohlc_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            ohlc_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            indicator_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            std_plt.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline', pen=self.cross_hair_pen), ignoreBounds=True)
            std_plt.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline', pen=self.cross_hair_pen), ignoreBounds=True)
            date_slicer.addItem(pg.InfiniteLine(angle=90, movable=False, name='vline'), ignoreBounds=True)
            date_slicer.addItem(pg.InfiniteLine(angle=0, movable=False, name='hline'), ignoreBounds=True)
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
        if 'i_std' in indicator:
            self.i_std = indicator['i_std']
            self.std_text = pg.TextItem(anchor=(0, 0))
            std_plt.addItem(self.std_text)

        plt_list = [ohlc_plt, indicator_plt, std_plt, date_slicer]

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
                        # if x_index == t_max + 1:
                        #     text_df = ticker_data.data.iloc[0]
                        # else:
                        #     text_df = market_data.data.iloc[x_index]
                        text_df = market_data.data.iloc[x_index]
                        html = f"""
                        <span style="color:white;font-size:12px"><span/><span style="color:blue">{str(text_df.name)[8:16].replace(" ", "日")}<span/><br/>
                        <span style="color:white;font-size:12px">开:<span/><span style="color:red">{text_df.open}<span/><br/>
                        <span style="color:white;font-size:12px">高:<span/><span style="color:red">{text_df.high}<span/><br/>
                        <span style="color:white;font-size:12px">低:<span/><span style="color:red">{text_df.low}<span/><br/>
                        <span style="color:white;font-size:12px">收:<span/><span style="color:red">{text_df.close}<span/>
                        """
                        self.info_text.setPos(ohlc_plt.getViewBox().viewRange()[0][0], ohlc_plt.getViewBox().viewRange()[1][1])
                        self.info_text.setHtml(html)
                        self.xaxis_text.setText(str(text_df.name))
                        self.yaxis_text.setText('{:.2f}'.format(mousePoint.y())) if inside else ...
                    except IndexError:
                        pass

                if self._at:
                    self.xaxis_text.setPos(x_index, ohlc_plt.vb.viewRange()[1][0])
                    self.yaxis_text.setPos(ohlc_plt.vb.viewRange()[0][1], mousePoint.y()) if inside else ...

                if 'i_ma' in indicator:
                    try:
                        ma_text = [f'<span style="color:rgb{MA_COLORS[k]};font-size:12px">MA{k[-2:]}:{round(getattr(self._i_ma, k)[x_index],2)}<span/>'
                                   for k, v in self._i_ma._windows.items()]
                        self.ma_text.setHtml('  '.join(ma_text))
                        self.ma_text.setPos(ohlc_plt.vb.viewRange()[0][1],ohlc_plt.vb.viewRange()[1][1])
                    except Exception:
                        pass

                if 'i_macd' in indicator:
                    try:
                        macd_text = f'<span style="color:red">MACD:{round(indicator["i_macd"].macd[x_index], 2)}<span/>  ' \
                                    f'<span style="color:yellow">DIFF:{round(indicator["i_macd"].diff[x_index], 2)}<span/>  ' \
                                    f'<span style="color:white">DEA:{round(indicator["i_macd"].dea[x_index], 2)}<span/>  '
                        self.macd_text.setHtml(macd_text)
                        self.macd_text.setPos(indicator_plt.vb.viewRange()[0][0], indicator_plt.vb.viewRange()[1][1])
                    except Exception:
                        pass

                if 'i_std' in indicator:
                    try:
                        std_text = f'<span style="color:yellow">INC:{round(indicator["i_std"].inc[x_index], 2)}<span/> ' \
                                   f'<span style="color:red">POS_STD:{round(indicator["i_std"].pos_std[x_index], 2)}<span/> ' \
                                   f'<span style="color:green">NEG_STD:{round(indicator["i_std"].neg_std[x_index], 2)}<span/> ' \
                                   f'<span style="color:white">RATIO:{round(indicator["i_std"].ratio[x_index], 2)}<span/> '
                        self.std_text.setHtml(std_text)
                        self.std_text.setPos(std_plt.vb.viewRange()[0][0], std_plt.vb.viewRange()[1][1])
                    except Exception:
                        pass
        return pg.SignalProxy(ohlc_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
