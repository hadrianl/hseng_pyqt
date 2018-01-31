#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/21 0021 11:49
# @Author  : Hadrianl 
# @File    : OHLC_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from data_visualize.baseitems import DateAxis, CandlestickItem
from data_handle.indicator import ma
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.Qt import QFont
import PyQt5
from data_fetch.util import *
import pandas as pd
from data_visualize.accessory import mouseaction


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
    def onPaint(self): ...


class OHlCWidget(KeyEventWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super(OHlCWidget,self).__init__(parent)
        self.setWindowTitle('实盘分钟图')
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
        self.ma_items_dict = {}
        self.macd_items_dict = {}

    def makePI(self, name):
        """生成PlotItem对象"""
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

    def binddata(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

    def init_ohlc(self):
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

    def init_ma(self):
        for w in self.i_ma._windows:  # 在主图表画出均线
            self.ma_items_dict[w] = self.ohlc_plt.plot(self.ohlc.timeindex, getattr(self.i_ma, w),
                                             pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))

    def init_indicator(self):
        self.indicator_plt = self.makePI('indicator')
        self.indicator_plt.setXLink('ohlc_plt')
        self.indicator_plt.setMaximumHeight(200)
        # pos_index = i_macd.to_df().macd >= 0
        # neg_index = i_macd.to_df().macd < 0
        macd_items_dict = self.macd_items_dict
        bar_line_type = pd.concat([self.i_macd.ohlc.close > self.i_macd.ohlc.open,
                                   self.i_macd.macd > 0], 1).apply(lambda x: (x.iloc[0] << 1) + x.iloc[1], 1)
        macd_items_dict['macd_pos>'] = pg.BarGraphItem(x=self.i_macd.timeindex[bar_line_type == 3],
                                                       height=self.i_macd.macd[bar_line_type == 3], width=0.5, brush='r')
        macd_items_dict['macd_neg>'] = pg.BarGraphItem(x=self.i_macd.timeindex[bar_line_type == 2],
                                                       height=self.i_macd.macd[bar_line_type == 2], width=0.5, brush='b')
        macd_items_dict['macd_pos<'] = pg.BarGraphItem(x=self.i_macd.timeindex[bar_line_type == 1],
                                                       height=self.i_macd.macd[bar_line_type == 1], width=0.5, brush='y')
        macd_items_dict['macd_neg<'] = pg.BarGraphItem(x=self.i_macd.timeindex[bar_line_type == 0],
                                                       height=self.i_macd.macd[bar_line_type == 0], width=0.5, brush='g')
        self.indicator_plt.addItem(macd_items_dict['macd_pos>'])
        self.indicator_plt.addItem(macd_items_dict['macd_neg>'])
        self.indicator_plt.addItem(macd_items_dict['macd_pos<'])
        self.indicator_plt.addItem(macd_items_dict['macd_neg<'])
        self.macd_items_dict['diff'] = self.indicator_plt.plot(self.i_macd.timeindex, self.i_macd.diff, pen='y')
        self.macd_items_dict['dea'] = self.indicator_plt.plot(self.i_macd.timeindex, self.i_macd.dea, pen='w')
        self.indicator_plt.showGrid(x=True, y=True)
        self.indicator_plt.hideAxis('bottom')
        self.indicator_plt.getViewBox().setXLink(self.ohlc_plt.getViewBox())  # 建立指标图表与主图表的viewbox连接
        self.main_layout.addItem(self.indicator_plt)
        self.main_layout.nextRow()

    def init_date_slice(self):
        self.date_slicer = self.makePI('date_slicer')
        self.date_slicer.hideAxis('right')
        self.date_slicer.setMaximumHeight(100)
        self.date_slicer.setMouseEnabled(False, False)
        self.close_curve = self.date_slicer.plot(self.ohlc.timeindex, self.ohlc.close)
        self.date_region = pg.LinearRegionItem([1, 100])
        # print(date_region.getRegion(), ohlc.close.min())
        # date_slicer.setLimits(xMin=data.timeindex.min(),
        #                       xMax=data.timeindex.max(),
        #                       yMin=data.close.min(),
        #                       yMax=data.close.max())
        self.date_slicer.addItem(self.date_region)
        self.main_layout.addItem(self.date_slicer)

    def init_mouseaction(self):
        self.mouse = mouseaction()
        self.proxy = self.mouse(self.ohlc_plt, self.indicator_plt, self.ohlc, self.tick_datas, i_ma=self.i_ma, i_macd=self.i_macd)

    def chart_replot(self):  # 重新画图
        ohlc = self.ohlc
        ohlcitems = self.ohlcitems
        ma_items_dict = self.ma_items_dict
        macd_items_dict = self.macd_items_dict
        i_macd = self.i_macd
        ohlc.update(self.tick_datas)
        ohlcitems.setData(ohlc)
        # -----------------------------均线----------------------------------------------+
        for w in ma_items_dict:
            ma_items_dict[w].setData(ohlc.timeindex.values, getattr(self.i_ma, w).values)
        # ----------------------------macd----------------------------------------------+
        # pos_index = i_macd.to_df().macd >= 0
        # neg_index = i_macd.to_df().macd < 0
        bar_line_type = pd.concat([i_macd.ohlc.close > i_macd.ohlc.open,
                                   i_macd.macd > 0], 1).apply(lambda x: (x.iloc[0] << 1) + x.iloc[1], 1)
        macd_items_dict['diff'].setData(i_macd.timeindex.values, i_macd.diff.values)
        macd_items_dict['dea'].setData(i_macd.timeindex.values, i_macd.dea.values)
        macd_items_dict['macd_pos>'].setOpts(x=i_macd.timeindex[bar_line_type == 3],
                                             height=i_macd.macd[bar_line_type == 3])
        macd_items_dict['macd_neg>'].setOpts(x=i_macd.timeindex[bar_line_type == 2],
                                             height=i_macd.macd[bar_line_type == 2])
        macd_items_dict['macd_pos<'].setOpts(x=i_macd.timeindex[bar_line_type == 1],
                                             height=i_macd.macd[bar_line_type == 1])
        macd_items_dict['macd_neg<'].setOpts(x=i_macd.timeindex[bar_line_type == 0],
                                             height=i_macd.macd[bar_line_type == 0])
        self.close_curve.setData(ohlc.timeindex.values, ohlc.close.values)
        self.xaxis.update_tickval(ohlc.timestamp)
        self.ohlc_data_update_sync()

    def ohlc_Yrange_update(self):
        ohlc_plt = self.ohlc_plt
        date_region = self.date_region
        ohlc = self.ohlc
        i_macd = self.i_macd
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
            self.date_slicer.setYRange(ohlc.close.min(), ohlc.close.max())
        except Exception as e:
            print('ohlc_Yrange_update', e)

    def date_slicer_update(self):  # 当时间切片发生变化时触发
        try:
            self.ohlc_plt.setXRange(*self.date_region.getRegion(), padding=0)
        except Exception as e:
            print('date_slicer_update', e)

    def ohlc_data_update_sync(self):
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

    def update_data_plot(self):
        tickitems = self.tickitems
        tick_datas = self.tick_datas
        # ---------------------------更新数据到图表----------------------------------------------------+
        if not tick_datas._ohlc_queue.empty():
            self.chart_replot()
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

    def init_signal(self):
        self.ohlc_plt.sigXRangeChanged.connect(self.ohlc_Yrange_update)
        self.date_region.sigRegionChanged.connect(self.date_slicer_update)
        self.tickitems.tick_signal.connect(self.update_data_plot)
        self.tick_datas.bindsignal(self.tickitems.tick_signal)

    def on_K_Up(self):
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length - length//7
        new_xrange = [self.mouse.x_index - new_length/2, self.mouse.x_index + new_length/2]
        print(self.mouse.x_index)
        if new_xrange[1] >= self.ohlc.timeindex.max():
            new_xrange = [self.ohlc.timeindex.max() + 4 - new_length, self.ohlc.timeindex.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)

    def on_K_Down(self):
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length + length//7
        new_xrange = [self.mouse.x_index - new_length / 2, self.mouse.x_index + new_length / 2]
        print(self.mouse.x_index)
        if new_xrange[1] >= self.ohlc.timeindex.max():
            new_xrange = [self.ohlc.timeindex.max() + 4 - new_length, self.ohlc.timeindex.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)