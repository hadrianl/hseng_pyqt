#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data
from data_handle.indicator import macd, ma
from data_visualize.baseitems import CandlestickItem, DateAxis
from data_visualize.Mainchart import mainchart
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_fetch.util import *

pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
data = market_data('2017-12-13','2017-12-18','HSIc1')
i_macd = macd(data)
i_ma = ma(data, 10, 20, 30,60)

app = QtWidgets.QApplication([])
win = pg.GraphicsWindow(border=0.5)
label = pg.LabelItem(jusitify='left')
win.addItem(label)
win.resize(1000,900)
# layout = pg.GraphicsLayout()
# view = pg.GraphicsView()
# view.setCentralItem(layout)
# view.show()
# view.setWindowTitle('恒指期货')
# view.resize(1200,800)

xaxis = DateAxis(data.timestamp, orientation='bottom')      ##时间坐标轴

ohlcitems = CandlestickItem()
ohlcitems.set_data(data)
ohlc_plt = win.addPlot(row=0,col=0, axisItems={'bottom': xaxis})    #添加主图表

ohlc_plt.addItem(ohlcitems)         #向主图表加入k线
ma_plt_dict = {}
for w in i_ma._windows:       ##在主图表画出均线
    ma_plt_dict['ma' + str(w)] = ohlc_plt.plot(data.timeindex, getattr(i_ma, 'ma' + str(w)), pen=pg.mkPen(color=MA_COLORS.get('ma' + str(w), 'w'), width=1))

ohlc_plt.setWindowTitle('market data')
ohlc_plt.showGrid(x=True, y=True)


indicator_plt = win.addPlot(row=1, col=0)     #添加指标图表
#-----------------------------画出指标-------------------------------+
win.nextRow()
pos_index = i_macd.to_df().macd >= 0
neg_index = i_macd.to_df().macd < 0
pos_macd = pg.BarGraphItem(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index], width=0.35, brush='r')
neg_macd = pg.BarGraphItem(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index], width=0.35, brush='g')
indicator_plt.addItem(pos_macd)
indicator_plt.addItem(neg_macd)
indicator_plt.plot(i_macd.diff, pen='y')
indicator_plt.plot(i_macd.dea, pen='w')
indicator_plt.showGrid(x=True, y=True)
indicator_plt.hideAxis('bottom')
indicator_plt.getViewBox().setXLink(ohlc_plt.getViewBox())    #建立指标图表与主图表的viewbox连接
#------------------------------------------------------------------+
#---------------添加时间切片图表-----------------------------------+
win.nextRow()
date_slicer = win.addPlot(row=2,col=0)
date_slicer.hideAxis('bottom')
date_slicer.setMouseEnabled(False, False)
date_slicer.plot(data.timeindex, data.close)
date_region = pg.LinearRegionItem([data.timeindex.max() - 200, data.timeindex.max()])
print(date_region.getRegion(),data.close.min())
date_slicer.setLimits(xMin=data.timeindex.min(),
                      xMax=data.timeindex.max(),
                      yMin=data.close.min(),
                      yMax=data.close.max())
date_slicer.addItem(date_region)
#------------------------------------------------------------------+
#-------------------------设置鼠标交互----------------------------+
vLine = pg.InfiniteLine(angle=90, movable=False)
hLine = pg.InfiniteLine(angle=0, movable=False)
ohlc_plt.addItem(vLine, ignoreBounds=True)
ohlc_plt.addItem(hLine, ignoreBounds=True)
vb = ohlc_plt.vb
def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    if ohlc_plt.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        # index = int(mousePoint.x())
        # if index > 1 and index < len(df1):
        #     hh=df1.iloc[index]
        #     label.setText(str(hh))
        vLine.setPos(mousePoint.x())
        hLine.setPos(mousePoint.y())
proxy = pg.SignalProxy(ohlc_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
#------------------------------------------------------------------+

def ohlc_Yrange_update():
    # global indicator_plt, date_region, ohlc_plt
    # rng = ohlc_plt.viewRange()[0]
    # rngMin = int(rng[0])
    # rngMax = int(rng[1])
    # indicator_plt.setXRange(rngMin, rngMax)
    viewrange = ohlc_plt.getViewBox().viewRange()
    date_region.setRegion(viewrange[0])
    # print(data.low[data.timestamp.between(*viewrange[0])].min(),
    #                     data.high[data.timestamp.between(*viewrange[0])].max())
    try:
        ohlc_plt.setYRange(data.low[data.timeindex.between(*viewrange[0])].min(),
                           data.high[data.timeindex.between(*viewrange[0])].max())
        indicator_plt.setYRange(i_macd.macd[i_macd.timeindex.between(*viewrange[0])].min(),
                            i_macd.macd[i_macd.timeindex.between(*viewrange[0])].max())
    except Exception as e:
        print(e)

def date_slicer_update():
    # global ohlc_plt, date_slicer
    ohlc_plt.setXRange(*date_region.getRegion(), padding=0)


date_region.sigRegionChanged.connect(date_slicer_update)
ohlc_plt.sigXRangeChanged.connect(ohlc_Yrange_update)
date_slicer_update()


# def update_data():
#     global  data, i_ma
#     data.update()
#     ohlcitems.set_data(data)
#     i_ma.update(data.data.iloc[-1])
#     for k, ma in ma_plt_dict.items():
#         ma.setdata(getattr(i_ma, k))
#     app.processEvents()

# timer = QtCore.QTimer()
# timer.timeout.connect(update_data)
# timer.start(1000)




if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()