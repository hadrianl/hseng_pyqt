#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/21 0021 11:49
# @Author  : Hadrianl 
# @File    : OHLC_ui.py
# @reference: uiKLine/uiKLine.py@moonnejs from github.com
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from data_visualize.baseitems import DateAxis, CandlestickItem, TradeDataScatter
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.Qt import QFont
import PyQt5
from data_fetch.util import *
import pandas as pd
from data_visualize.accessory import mouseaction
import numpy as np
from threading import Thread
from datetime import datetime
import time


class KeyEventWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMouseTracking(True)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        if a0.key() == QtCore.Qt.Key_Up:
            self.on_K_Up()
        elif a0.key() == QtCore.Qt.Key_Down:
            self.on_K_Down()
        elif a0.key() == QtCore.Qt.Key_Left:
            self.on_K_Left()
        elif a0.key() == QtCore.Qt.Key_Right:
            self.on_K_Right()

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_RightClick(a0.pos())
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_LeftClick(a0.pos())

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_RightRelease(a0.pos())
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_LeftRelease(a0.pos())

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_Right_Double_Click()
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_Left_Double_Click()
    # def wheelEvent(self, a0: QtGui.QWheelEvent):
    #     if a0.angleDelta() > 0:
    #         self.on_M_WheelUp()
    #     else:
    #         self.on_M_WheelDown()

    def paintEvent(self, a0: QtGui.QPaintEvent):
        self.onPaint()

    def on_K_Up(self): ...
    def on_K_Down(self): ...
    def on_K_Left(self): ...
    def on_K_Right(self): ...
    def on_M_RightClick(self, pos): ...
    def on_M_LeftClick(self, pos): ...
    def on_M_RightRelease(self, pos): ...
    def on_M_LeftRelease(self, pos): ...
    def on_M_WheelUp(self): ...
    def on_M_WheelDown(self): ...
    def on_M_Right_Double_Click(self): ...
    def on_M_Left_Double_Click(self): ...
    def onPaint(self): ...


class OHlCWidget(KeyEventWidget):

    sig_M_Left_Double_Click = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        self.parent = parent
        super(OHlCWidget, self).__init__(parent)
        self.pw = pg.PlotWidget()
        self.main_layout = pg.GraphicsLayout(border=(100, 100, 100))
        self.main_layout.setGeometry(QtCore.QRectF(10, 10, 1200, 700))
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.pw.setCentralItem(self.main_layout)
        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(self.pw)
        self.setLayout(self.vb)
        self.xaxis = DateAxis({}, orientation='bottom')

    def makePI(self, name):  # 生成PlotItem的工厂函数
        # vb = CustomViewBox()
        plotItem = pg.PlotItem(viewBox=pg.ViewBox(), name=name, axisItems={'bottom': self.xaxis})
        plotItem.setMenuEnabled(False)
        # plotItem.setClipToView(True)
        plotItem.hideAxis('left')
        plotItem.showAxis('right')
        plotItem.setDownsampling(mode='peak')
        # # plotItem.setRange(xRange=(0, 1), yRange=(0, 1))
        plotItem.getAxis('right').setWidth(40)
        plotItem.getAxis('right').setStyle(tickFont=QFont("Roman times", 10, QFont.Bold))
        plotItem.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        plotItem.showGrid(True, True)
        plotItem.hideButtons()
        return plotItem

    def binddata(self, **data):  # 实现数据与UI界面的绑定
        for k, v in data.items():
            setattr(self, k, v)

    def init_ohlc(self):  # 初始化主图OHLC k线
        self.ohlc_plt = self.makePI('ohlc')
        self.ohlc_plt.setMinimumHeight(300)
        self.ohlcitems = CandlestickItem()
        self.ohlcitems.setData(self.ohlc)
        self.ohlc_plt.addItem(self.ohlcitems)
        self.ohlc_plt.setWindowTitle('market data')
        self.ohlc_plt.showGrid(x=True, y=True)
        self.tickitems = CandlestickItem()
        self.tickitems.mark_line()
        self.ohlc_plt.addItem(self.tickitems)
        self.ohlc_plt.addItem(self.tickitems.hline)
        self.main_layout.addItem(self.ohlc_plt)
        self.main_layout.nextRow()

    def init_ma(self):  # 初始化主图均线ma
        self.ma_items_dict = {}
        for w in self.i_ma._windows:
            self.ma_items_dict[w] = self.ohlc_plt.plot(self.ohlc.timeindex, getattr(self.i_ma, w),
                                             pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))

    def init_indicator(self):  # 初始化指标图
        self.macd_items_dict = {}
        self.indicator_plt = self.makePI('indicator')
        # self.indicator_plt.setXLink('ohlc')
        self.indicator_plt.setMaximumHeight(150)
        macd_pens = pd.concat([self.i_macd.ohlc.close > self.i_macd.ohlc.open,self.i_macd.macd > 0], 1).\
            apply(lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map({3: 'r', 2: 'b', 1:'y', 0: 'g'})
        macd_brushs = [None if (self.i_macd.macd > self.i_macd.macd.shift(1))[i]
                       else v for i, v in macd_pens.iteritems()]
        self.macd_items_dict['Macd'] = pg.BarGraphItem(x=self.i_macd.timeindex, height=self.i_macd.macd,
                                                       width=0.5, pens=macd_pens, brushes=macd_brushs)
        self.indicator_plt.addItem(self.macd_items_dict['Macd'])
        self.macd_items_dict['diff'] = self.indicator_plt.plot(self.i_macd.timeindex, self.i_macd.diff, pen='y')
        self.macd_items_dict['dea'] = self.indicator_plt.plot(self.i_macd.timeindex, self.i_macd.dea, pen='w')
        self.indicator_plt.showGrid(x=True, y=True)
        self.indicator_plt.hideAxis('bottom')
        self.indicator_plt.getViewBox().setXLink(self.ohlc_plt.getViewBox())  # 建立指标图表与主图表的viewbox连接
        self.main_layout.addItem(self.indicator_plt)
        self.main_layout.nextRow()

    def init_std(self):
        self.std_items_dict = {}
        self.std_plt = self.makePI('std')
        # self.std_plt.setXLink('ohlc')
        self.std_plt.setMaximumHeight(150)
        self.brushes = std_brushes = pd.concat([self.i_std.inc > self.i_std.pos_std,
                                self.i_std.inc < self.i_std.neg_std], 1)\
            .apply(lambda x: {2: 'r', 1: 'b', 0: 'y'}[(x.iloc[0]<<1) + x.iloc[1]], 1)
        self.std_items_dict['inc'] = pg.BarGraphItem(x=self.i_std.timeindex, height=self.i_std.inc,
                                                     width=0.5, brushes=std_brushes)
        self.std_plt.addItem(self.std_items_dict['inc'])
        self.std_items_dict['pos_std'] = self.std_plt.plot(self.i_std.timeindex, self.i_std.pos_std, pen='r')
        self.std_items_dict['neg_std'] = self.std_plt.plot(self.i_std.timeindex, self.i_std.neg_std, pen='g')
        self.std_plt.hideAxis('bottom')
        self.std_plt.getViewBox().setXLink(self.ohlc_plt.getViewBox())
        self.main_layout.addItem(self.std_plt)
        self.main_layout.nextRow()

    def init_trade_data(self):  # todo tradedata
        self.tradeitems = TradeDataScatter('b')
        print(self.trade_data['OpenTime'], self.trade_data['OpenPrice'])
        self.tradeitems.setData(x=self.trade_data['OpenTime'], y=self.trade_data['OpenPrice'])
        self.ohlc_plt.addItem(self.tradeitems)

    def init_date_slice(self):  # 初始化时间切片图
        self.date_slicer = self.makePI('date_slicer')
        self.date_slicer.hideAxis('right')
        self.date_slicer.setMaximumHeight(80)
        self.date_slicer.setMouseEnabled(False, False)
        self.close_curve = self.date_slicer.plot(self.ohlc.timeindex, self.ohlc.close)
        self.date_region = pg.LinearRegionItem([1, 100])
        self.date_slicer.addItem(self.date_region)
        self.main_layout.addItem(self.date_slicer)

    def init_mouseaction(self):  # 初始化鼠标十字光标动作以及光标所在位置的信息
        self.mouse = mouseaction()
        self.proxy = self.mouse(self.ohlc_plt, self.indicator_plt, self.std_plt, self.date_slicer, self.ohlc, self.tick_datas,
                                i_ma=self.i_ma, i_macd=self.i_macd, i_std=self.i_std)

    def init_buttons(self):
        self.consolebutton = QtWidgets.QPushButton(text='交互console',parent=self.pw)
        self.consolebutton.setGeometry(QtCore.QRect(10, 250, 75, 23))

    def chart_replot(self, last_ohlc_data):  # 重新画图
        ohlc = self.ohlc
        ohlcitems = self.ohlcitems
        ma_items_dict = self.ma_items_dict
        macd_items_dict = self.macd_items_dict
        std_items_dict = self.std_items_dict
        i_macd = self.i_macd
        ohlc.update(last_ohlc_data)
        ohlcitems.setData(ohlc)
        # -----------------------------均线----------------------------------------------+
        for w in ma_items_dict:
            ma_items_dict[w].setData(ohlc.timeindex.values, getattr(self.i_ma, w).values)
        # ----------------------------Macd----------------------------------------------+
        macd_items_dict['diff'].setData(i_macd.timeindex.values, i_macd.diff.values)
        macd_items_dict['dea'].setData(i_macd.timeindex.values, i_macd.dea.values)
        macd_pens = pd.concat(
            [self.i_macd.ohlc.close > self.i_macd.ohlc.open,
             self.i_macd.macd > 0], 1).apply(
            lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map({3: 'r', 2: 'b', 1: 'y', 0: 'g'})
        macd_brushes = [None if (self.i_macd.macd > self.i_macd.macd.shift(1))[i]
                       else v for i, v in macd_pens.iteritems()]
        self.macd_items_dict['Macd'].setOpts(x=i_macd.timeindex, height=i_macd.macd, pens=macd_pens, brushes=macd_brushes)
        # ----------------------------std-------------------------------------------------+
        self.brushes = std_brushes = pd.concat(
            [self.i_std.inc > self.i_std.pos_std,
             self.i_std.inc < self.i_std.neg_std], 1).apply(
            lambda x: {2: 'r', 1: 'b', 0: 'y'}[(x.iloc[0]<<1) + x.iloc[1]], 1)
        std_items_dict['pos_std'].setData(self.i_std.timeindex, self.i_std.pos_std)
        std_items_dict['neg_std'].setData(self.i_std.timeindex, self.i_std.neg_std)
        std_items_dict['inc'].setOpts(x=self.i_std.timeindex, height=self.i_std.inc, brushes=std_brushes)

        self.close_curve.setData(ohlc.timeindex.values, ohlc.close.values)
        self.xaxis.update_tickval(ohlc.timestamp)
        self.ohlc_data_update_sync()

    def ohlc_Yrange_update(self):  # 更新主图和指标图的高度
        ohlc_plt = self.ohlc_plt
        date_region = self.date_region
        ohlc = self.ohlc
        i_macd = self.i_macd
        i_std = self.i_std
        viewrange = ohlc_plt.getViewBox().viewRange()
        date_region.setRegion(viewrange[0])
        try:
            ohlc_plt.setYRange(ohlc.low[ohlc.timeindex.between(*viewrange[0])].min(),
                               ohlc.high[ohlc.timeindex.between(*viewrange[0])].max())
            self.indicator_plt.setYRange(min(i_macd.macd[i_macd.timeindex.between(*viewrange[0])].min(),
                                             i_macd.diff[i_macd.timeindex.between(*viewrange[0])].min(),
                                             i_macd.dea[i_macd.timeindex.between(*viewrange[0])].min()),
                                         max(i_macd.macd[i_macd.timeindex.between(*viewrange[0])].max(),
                                             i_macd.diff[i_macd.timeindex.between(*viewrange[0])].max(),
                                             i_macd.dea[i_macd.timeindex.between(*viewrange[0])].max())
                                         )
            self.std_plt.setYRange(min(i_std.inc[i_std.timeindex.between(*viewrange[0])].min(),
                                       i_std.neg_std[i_std.timeindex.between(*viewrange[0])].min()),
                                   max(i_std.inc[i_std.timeindex.between(*viewrange[0])].max(),
                                       i_std.pos_std[i_std.timeindex.between(*viewrange[0])].max()))
            self.date_slicer.setYRange(ohlc.close.min(), ohlc.close.max())
        except Exception as e:
            print('ohlc_Yrange_update', e)

    def date_slicer_update(self):  # 当时间切片发生变化时触发
        try:
            self.ohlc_plt.setXRange(*self.date_region.getRegion(), padding=0)
        except Exception as e:
            print('date_slicer_update', e)

    def ohlc_data_update_sync(self):  # 主图横坐标变化的实现
        date_region = self.date_region
        ohlc = self.ohlc
        date_region_Max = int(date_region.getRegion()[1])
        date_region_len = int(date_region.getRegion()[1] - date_region.getRegion()[0])
        print(f'可视区域最大值：{date_region_Max}')
        print(f'图表timeindex最大值：{ohlc.timeindex.max()}')
        if len(ohlc.data) >= ohlc.bar_size:
            if date_region_Max == ohlc.timeindex.max() + 3:  # 判断最新数据是否是在图表边缘
                date_region.setRegion([ohlc.timeindex.max() + 3 - date_region_len, ohlc.timeindex.max() + 3])
            else:
                date_region.setRegion([date_region_Max - date_region_len - 1, date_region_Max - 1])
        else:
            if date_region_Max == ohlc.timeindex.max() + 3:  # 判断最新数据是否是在图表边缘
                date_region.setRegion([ohlc.timeindex.max() + 4 - date_region_len, ohlc.timeindex.max() + 4])
            else:
                date_region.setRegion([date_region_Max - date_region_len, date_region_Max])
        self.ohlc_Yrange_update()
        self.ohlc_plt.update()

    def update_data_plot(self):  # 当前K线根据ticker数据的更新
        tickitems = self.tickitems
        tick_datas = self.tick_datas
        # ---------------------------更新数据到图表----------------------------------------------------+
        tickitems.update()
        tick_datas._timeindex = self.ohlc.timeindex.iloc[-1] + 1
        tickitems.setData(tick_datas)
        tickitems.update()
        # ---------------------------调整画图界面高度----------------------------------------------------+
        viewrange = self.ohlc_plt.getViewBox().viewRange()
        if tick_datas.high.iloc[0] >= viewrange[1][1] or tick_datas.low.iloc[0] <= viewrange[1][0]:
            self.ohlc_plt.setYRange(min(viewrange[1][0], tick_datas.low.iloc[0]),
                                    max(viewrange[1][1], tick_datas.high.iloc[0]))
        # app.processEvents()

    def init_signal(self):  # 信号的连接与绑定
        self.ohlc_plt.sigXRangeChanged.connect(self.ohlc_Yrange_update)
        self.date_region.sigRegionChanged.connect(self.date_slicer_update)
        self.tickitems.tick_signal.connect(self.update_data_plot)
        self.tickitems.ohlc_replot_signal.connect(self.chart_replot)
        self.tick_datas.bindsignal(self.tickitems.tick_signal, self.tickitems.ohlc_replot_signal)

    def on_K_Up(self):  # 键盘up键触发，放大
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length - length//7
        new_xrange = [self.mouse.x_index - new_length/2, self.mouse.x_index + new_length/2]
        if new_xrange[1] >= self.ohlc.timeindex.max():
            new_xrange = [self.ohlc.timeindex.max() + 4 - new_length, self.ohlc.timeindex.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)

    def on_K_Down(self):  # 键盘down键触发，缩小
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length + length//7
        new_xrange = [self.mouse.x_index - new_length / 2, self.mouse.x_index + new_length / 2]
        if new_xrange[1] >= self.ohlc.timeindex.max():
            new_xrange = [self.ohlc.timeindex.max() + 4 - new_length, self.ohlc.timeindex.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)

    def on_M_Right_Double_Click(self):  # 鼠标右键双击触发，跳转到当前视图
        self.ohlc_plt.setXRange(self.ohlc.timeindex.max() - 120, self.ohlc.timeindex.max() + 3)

    def on_M_Left_Double_Click(self):
        self.sig_M_Left_Double_Click.emit()
