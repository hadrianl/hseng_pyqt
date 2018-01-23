#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data
from data_handle.indicator import macd, ma
from data_handle.tickdata import tickdatas
from data_visualize.baseitems import CandlestickItem, DateAxis
from data_visualize.accessory import mouseaction
from data_visualize.Mainchart import mainchart
import datetime as dt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_fetch.util import *
from pyqtgraph.dockarea import *
from numpy.random import random
import time

pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
start_time = dt.datetime.now() - dt.timedelta(minutes=60)
end_time = dt.datetime.now() + dt.timedelta(minutes=10)
data = market_data(start_time, end_time, 'HSIF8')
i_macd = macd(short=10, long=22, m=9)
i_ma = ma(ma10=10, ma20=20, ma30=30, ma60=60)
data.indicator_register(i_ma)
data.indicator_register(i_macd)
# -----------------------------------------------------------------------+
# -----------------------窗口与app初始化---------------------------------+
app = QtWidgets.QApplication([])
win = QtGui.QMainWindow()
layout = pg.GraphicsLayout()
area = DockArea()
win.setCentralWidget(area)
win.resize(1500, 900)
win.show()
d1 =Dock('mainchart', size=(1, 1))
mainchart_dock = Dock('恒指期货', hideTitle=True, size=(1200, 600))
indicator_dock = Dock('指标', size=(1200, 150))
date_slicer_dock = Dock('slicer', size=(1200, 100), hideTitle=True)
date_slicer_dock.hideTitleBar()
area.addDock(d1, 'left')
area.addDock(mainchart_dock, 'right')
area.addDock(indicator_dock, 'bottom', mainchart_dock)
area.addDock(date_slicer_dock, 'bottom', indicator_dock)
# -----------------------------------------------------------------------+
xaxis = DateAxis(data.timestamp, orientation='bottom')  # 时间坐标轴
ohlc_plt = pg.PlotWidget(axisItems={'bottom': xaxis})    # 添加主图表
ohlcitems = CandlestickItem()
ohlcitems.setData(data)
ohlc_plt.addItem(ohlcitems)         # 向主图表加入k线
ma_items_dict = {}
for w in i_ma._windows:       # 在主图表画出均线
    ma_items_dict[w] = ohlc_plt.plot(data.timeindex, getattr(i_ma, w), pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
ohlc_plt.setWindowTitle('market data')
ohlc_plt.showGrid(x=True, y=True)
# ----------------------------tick-------------------------------+
tickitems = CandlestickItem()
ohlc_plt.addItem(tickitems)

# -------------------------------------------------------------------+

# ----------------------------画出指标-------------------------------+
# main_chart_layout.nextRow()
indicator_plt = pg.PlotWidget()     # 添加指标图表
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
# ------------------------------------------------------------------+
# ---------------添加时间切片图表-----------------------------------+
# main_chart_layout.nextRow()
date_slicer = pg.PlotWidget()
date_slicer.hideAxis('bottom')
date_slicer.setMouseEnabled(False, False)
close_curve = date_slicer.plot(data.timeindex, data.close)
date_region = pg.LinearRegionItem([data.timeindex.max() - 150, data.timeindex.max() + 10])
print(date_region.getRegion(), data.close.min())
# date_slicer.setLimits(xMin=data.timeindex.min(),
#                       xMax=data.timeindex.max(),
#                       yMin=data.close.min(),
#                       yMax=data.close.max())
date_slicer.addItem(date_region)
# ------------------------------------------------------------------+
# -------------------------设置标签----------------------------+
# legendItem = pg.LegendItem((40,10),(30,30))
# legendItem.addItem(macd_items_dict['diff'],'diff')

# ------------------------------------------------------------------+
w1 = pg.LayoutWidget()
label = QtGui.QLabel(""" -- DockArea Example -- 
This window has 6 Dock widgets in it. Each dock can be dragged
by its title bar to occupy a different space within the window 
but note that one dock has its title bar hidden). Additionally,
the borders between docks may be dragged to resize. Docks that are dragged on top
of one another are stacked in a tabbed layout. Double-click a dock title
bar to place it in its own window.
""")
saveBtn = QtGui.QPushButton('Save dock state')
restoreBtn = QtGui.QPushButton('Restore dock state')
restoreBtn.setEnabled(False)
w1.addWidget(label, row=0, col=0)
w1.addWidget(saveBtn, row=1, col=0)
w1.addWidget(restoreBtn, row=2, col=0)
d1.addWidget(w1)
state = None
def save():
    global state
    state = area.saveState()
    restoreBtn.setEnabled(True)
def load():
    global state
    area.restoreState(state)
saveBtn.clicked.connect(save)
restoreBtn.clicked.connect(load)

mainchart_dock.addWidget(ohlc_plt)
indicator_dock.addWidget(indicator_plt)
date_slicer_dock.addWidget(date_slicer)


def ohlc_Yrange_update():
    viewrange = ohlc_plt.getViewBox().viewRange()
    date_region.setRegion(viewrange[0])
    try:
        ohlc_plt.setYRange(data.low[data.timeindex.between(*viewrange[0])].min(),
                           data.high[data.timeindex.between(*viewrange[0])].max())
        indicator_plt.setYRange(i_macd.macd[i_macd.timeindex.between(*viewrange[0])].min(),
                            i_macd.macd[i_macd.timeindex.between(*viewrange[0])].max())
        date_slicer.setYRange(data.close.min(), data.close.max())
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
    print(f'图表timeindex最大值：{data.timeindex.max()}')
    if date_region_Max == data.timeindex.max() + 3:    # 判断最新数据是否是在图表边缘
        date_region.setRegion([data.timeindex.max() + 3 - date_region_len, data.timeindex.max() + 3])
        ohlc_Yrange_update()
    else:
        date_region.setRegion([date_region_Max - date_region_len-1, date_region_Max-1])
    ohlc_plt.update()


def update_data_plot():
    global data, pos_index, neg_index, tick_datas, ohlc_plt
    tickitems.update()
    tick_datas._timeindex = data.timeindex.iloc[-1] + 1
    tickitems.setData(tick_datas)
    tickitems.update()

    # ---------------------------调整画图界面高度----------------------------------------------------+
    viewrange = ohlc_plt.getViewBox().viewRange()
    if tick_datas.high.iloc[0] >= viewrange[1][1] or tick_datas.low.iloc[0] <= viewrange[1][0]:
        ohlc_plt.setYRange(min(viewrange[1][0], tick_datas.low.iloc[0]),
                           max(viewrange[1][1], tick_datas.high.iloc[0]))

    # ---------------------------更新数据到图表----------------------------------------------------+
    if not tick_datas._ohlc_queue.empty():
        data.update(tick_datas)
        ohlcitems.setData(data)

        for w in ma_items_dict:
            ma_items_dict[w].setData(data.timeindex.values, getattr(i_ma, w).values)
        pos_index = i_macd.to_df().macd >= 0
        neg_index = i_macd.to_df().macd < 0
        macd_items_dict['diff'].setData(i_macd.timeindex.values, i_macd.diff.values)
        macd_items_dict['dea'].setData(i_macd.timeindex.values, i_macd.dea.values)
        macd_items_dict['macd_pos'].setOpts(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index])
        macd_items_dict['macd_neg'].setOpts(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index])
        close_curve.setData(data.timeindex.values, data.close.values)
        xaxis.update_tickval(data.timestamp)
    # ------------------------------------------------------------------------------------------------+
        ohlc_data_update_sync()
    app.processEvents()
tick_datas = tickdatas('HSIF8')
tick_datas.bindsignal(tickitems.tick_signal)
tick_datas.active()
tickitems.tick_signal.connect(update_data_plot)

# -------------------------设置鼠标交互----------------------------+
mouse = mouseaction()
proxy = mouse(ohlc_plt, data, tick_datas)
# ------------------------------------------------------------------+


date_slicer_update()



if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()
