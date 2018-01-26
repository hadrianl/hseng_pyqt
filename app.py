#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC, NewOHLC
from data_handle.indicator import macd, ma
from data_visualize.baseitems import CandlestickItem, DateAxis
from data_visualize.accessory import mouseaction
from data_visualize.OHLC_ui import OHlCWidget
import datetime as dt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_fetch.util import *
from pyqtgraph.dockarea import *
from numpy.random import random
import time
from PyQt5.Qt import QFont
from mainwindow import Ui_MainWindow
import sys

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    global xaxis
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)

pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
start_time = dt.datetime.now() - dt.timedelta(minutes=120)
end_time = dt.datetime.now() + dt.timedelta(minutes=10)
ohlc = OHLC(start_time, end_time, 'HSIF8')
i_macd = macd(short=10, long=22, m=9)
i_ma = ma(ma10=10, ma20=20, ma30=30, ma60=60)
ohlc + i_ma
ohlc + i_macd

# -----------------------------------------------------------------------+
# -----------------------窗口与app初始化---------------------------------+
app = QtWidgets.QApplication(sys.argv)
xaxis = DateAxis(ohlc.timestamp, orientation='bottom')  # 时间坐标轴
# win = MainWindow()
win = pg.PlotWidget()
layout = pg.GraphicsLayout(border=(100,100,100))
layout.setGeometry(QtCore.QRectF(10, 10, 1200, 700))
layout.setContentsMargins(10, 10, 10, 10)
layout.setSpacing(0)
layout.setBorder(color=(255, 255, 255, 255), width=0.8)
win.setCentralItem(layout)
# win = QtGui.QMainWindow()
# layout = pg.GraphicsLayout()
# area = DockArea()
# win.setCentralWidget(area)
# win.resize(1500, 900)
# win.show()
# d1 =Dock('mainchart', size=(1, 1))
# mainchart_dock = Dock('恒指期货', hideTitle=True, size=(1200, 600))
# indicator_dock = Dock('指标', size=(1200, 150))
# date_slicer_dock = Dock('slicer', size=(1200, 100), hideTitle=True)
# date_slicer_dock.hideTitleBar()
# area.addDock(d1, 'left')
# area.addDock(mainchart_dock, 'right')
# area.addDock(indicator_dock, 'bottom', mainchart_dock)
# area.addDock(date_slicer_dock, 'bottom', indicator_dock)

# ohlc_plt = win.ohlc_plt
# indicator_plt = win.indicator_plt
# date_slicer = win.date_slicer

# -----------------------------------------------------------------------+
def makePI(name):
    """生成PlotItem对象"""
    # vb = CustomViewBox()
    global xaxis
    plotItem = pg.PlotItem(viewBox=pg.ViewBox(), name=name, axisItems={'bottom': xaxis})
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
# ohlc_plt = pg.PlotWidget(win.centralwidget, axisItems={'bottom': xaxis})    # 添加主图表
# ohlc_plt = pg.PlotItem(viewBox=pg.ViewBox(), name='ohlc', axisItems={'bottom': xaxis})
ohlc_plt = makePI('ohlc')
# ohlc_plt.setXLink('date_slicer')
ohlc_plt.setMinimumHeight(300)
ohlcitems = CandlestickItem()
ohlcitems.setData(ohlc)
ohlc_plt.addItem(ohlcitems)         # 向主图表加入k线
ma_items_dict = {}
for w in i_ma._windows:       # 在主图表画出均线
    ma_items_dict[w] = ohlc_plt.plot(ohlc.timeindex, getattr(i_ma, w), pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
ohlc_plt.setWindowTitle('market data')
ohlc_plt.showGrid(x=True, y=True)
# ----------------------------tick-------------------------------+
tickitems = CandlestickItem()
ohlc_plt.addItem(tickitems)
layout.addItem(ohlc_plt)
layout.nextRow()
# -------------------------------------------------------------------+

# ----------------------------画出指标-------------------------------+
# main_chart_layout.nextRow()
# indicator_plt = pg.PlotWidget()     # 添加指标图表
# indicator_plt = pg.PlotItem(viewBox=pg.ViewBox(), name='ohlc', axisItems={'bottom': xaxis})
indicator_plt = makePI('indicator')
indicator_plt.setXLink('ohlc_plt')
indicator_plt.setMaximumHeight(200)
pos_index = i_macd.to_df().macd >= 0
neg_index = i_macd.to_df().macd < 0
macd_items_dict = dict()
macd_items_dict['macd_pos'] = pg.BarGraphItem(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index], width=0.35, brush='r')
macd_items_dict['macd_neg'] = pg.BarGraphItem(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index], width=0.35, brush='g')
indicator_plt.addItem(macd_items_dict['macd_pos'])
indicator_plt.addItem(macd_items_dict['macd_neg'])
macd_items_dict['diff'] = indicator_plt.plot(i_macd.timeindex, i_macd.diff, pen='y')
macd_items_dict['dea'] = indicator_plt.plot(i_macd.timeindex, i_macd.dea, pen='w')
indicator_plt.showGrid(x=True, y=True)
indicator_plt.hideAxis('bottom')
indicator_plt.getViewBox().setXLink(ohlc_plt.getViewBox())    # 建立指标图表与主图表的viewbox连接
layout.addItem(indicator_plt)
layout.nextRow()
# ------------------------------------------------------------------+
# ---------------添加时间切片图表-----------------------------------+

# date_slicer = pg.PlotItem(viewBox=pg.ViewBox(), name='date_slicer', axisItems={'bottom': xaxis})
date_slicer = makePI('date_slicer')
date_slicer.hideAxis('right')
date_slicer.setMaximumHeight(100)
date_slicer.setMouseEnabled(False, False)
close_curve = date_slicer.plot(ohlc.timeindex, ohlc.close)
date_region = pg.LinearRegionItem([1, 100])
print(date_region.getRegion(), ohlc.close.min())
# date_slicer.setLimits(xMin=data.timeindex.min(),
#                       xMax=data.timeindex.max(),
#                       yMin=data.close.min(),
#                       yMax=data.close.max())
date_slicer.addItem(date_region)
layout.addItem(date_slicer)
# ------------------------------------------------------------------+
# -------------------------设置标签----------------------------+
# legendItem = pg.LegendItem((40,10),(30,30))
# legendItem.addItem(macd_items_dict['diff'],'diff')

# ------------------------------------------------------------------+
# mainchart_dock.addWidget(ohlc_plt)
# indicator_dock.addWidget(indicator_plt)
# date_slicer_dock.addWidget(date_slicer)
# win.verticalLayout.addWidget(ohlc_plt)
# win.verticalLayout_2.addWidget(indicator_plt)
# win.verticalLayout_3.addWidget(date_slicer)

def ohlc_Yrange_update():
    viewrange = ohlc_plt.getViewBox().viewRange()
    date_region.setRegion(viewrange[0])
    try:
        ohlc_plt.setYRange(ohlc.low[ohlc.timeindex.between(*viewrange[0])].min(),
                           ohlc.high[ohlc.timeindex.between(*viewrange[0])].max())
        indicator_plt.setYRange(i_macd.macd[i_macd.timeindex.between(*viewrange[0])].min(),
                            i_macd.macd[i_macd.timeindex.between(*viewrange[0])].max())
        date_slicer.setYRange(ohlc.close.min(), ohlc.close.max())
    except Exception as e:
        print('ohlc_Yrange_update', e)
ohlc_plt.sigXRangeChanged.connect(ohlc_Yrange_update)

def date_slicer_update():  # 当时间切片发生变化时触发
    try:
        ohlc_plt.setXRange(*date_region.getRegion(), padding=0)
    except Exception as e:
        print('date_slicer_update', e)
date_region.sigRegionChanged.connect(date_slicer_update)

def ohlc_data_update_sync():
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
    ohlc_Yrange_update()
    ohlc_plt.update()


def update_data_plot():
    global ohlc, pos_index, neg_index, tick_datas, ohlc_plt
    tickitems.update()
    tick_datas._timeindex = ohlc.timeindex.iloc[-1] + 1
    tickitems.setData(tick_datas)
    tickitems.update()

    # ---------------------------调整画图界面高度----------------------------------------------------+
    viewrange = ohlc_plt.getViewBox().viewRange()
    if tick_datas.high.iloc[0] >= viewrange[1][1] or tick_datas.low.iloc[0] <= viewrange[1][0]:
        ohlc_plt.setYRange(min(viewrange[1][0], tick_datas.low.iloc[0]),
                           max(viewrange[1][1], tick_datas.high.iloc[0]))

    # ---------------------------更新数据到图表----------------------------------------------------+
    if not tick_datas._ohlc_queue.empty():
        ohlc.update(tick_datas)
        ohlcitems.setData(ohlc)

        for w in ma_items_dict:
            ma_items_dict[w].setData(ohlc.timeindex.values, getattr(i_ma, w).values)
        pos_index = i_macd.to_df().macd >= 0
        neg_index = i_macd.to_df().macd < 0
        macd_items_dict['diff'].setData(i_macd.timeindex.values, i_macd.diff.values)
        macd_items_dict['dea'].setData(i_macd.timeindex.values, i_macd.dea.values)
        macd_items_dict['macd_pos'].setOpts(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index])
        macd_items_dict['macd_neg'].setOpts(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index])
        close_curve.setData(ohlc.timeindex.values, ohlc.close.values)
        xaxis.update_tickval(ohlc.timestamp)
    # ------------------------------------------------------------------------------------------------+
        ohlc_data_update_sync()
    app.processEvents()
tickitems.tick_signal.connect(update_data_plot)
tick_datas = NewOHLC('HSIF8')
tick_datas.bindsignal(tickitems.tick_signal)
tick_datas.active()
# -------------------------设置鼠标交互----------------------------+
mouse = mouseaction()
proxy = mouse(ohlc_plt, ohlc, tick_datas)
# ------------------------------------------------------------------+

date_region.setRegion([ohlc.timeindex.max() - 120, ohlc.timeindex.max() + 4])  # 初始化可视区域
tick_datas._timeindex = ohlc.timeindex.iloc[-1] + 1


if __name__ == '__main__':
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())
