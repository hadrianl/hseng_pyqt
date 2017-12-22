#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import market_data, new_market_data
from data_handle.indicator import macd, ma
from data_visualize.baseitems import CandlestickItem, DateAxis
from data_visualize.Mainchart import mainchart
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_fetch.util import *

pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
data = market_data('2017-12-12','2017-12-14 21:00:00','HSIc1')
i_macd = macd(short=10, long=22, m=9)
i_ma = ma(ma10=10, ma20=20, ma30=30,ma60=60)
data.indicator_register(i_ma)
data.indicator_register(i_macd)


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
xaxis = DateAxis(data.timestamp, orientation='bottom')##时间坐标轴

ohlcitems = CandlestickItem()
ohlcitems.set_data(data)
ohlc_plt = win.addPlot(row=0,col=0, axisItems={'bottom': xaxis})    #添加主图表


ohlc_plt.addItem(ohlcitems)         #向主图表加入k线
ma_items_dict = {}
for w in i_ma._windows:       ##在主图表画出均线
    ma_items_dict[w] = ohlc_plt.plot(data.timeindex, getattr(i_ma, w), pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
    # print(type(ma_items_dict[w]))
ohlc_plt.setWindowTitle('market data')
ohlc_plt.showGrid(x=True, y=True)


indicator_plt = win.addPlot(row=1, col=0)     #添加指标图表
#-----------------------------画出指标-------------------------------+
win.nextRow()
pos_index = i_macd.to_df().macd >= 0
neg_index = i_macd.to_df().macd < 0
macd_items_dict ={}
macd_items_dict['macd_pos'] = pg.BarGraphItem(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index], width=0.35, brush='r')
macd_items_dict['macd_neg'] = pg.BarGraphItem(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index], width=0.35, brush='g')
indicator_plt.addItem(macd_items_dict['macd_pos'])
indicator_plt.addItem(macd_items_dict['macd_neg'])
macd_items_dict['diff'] = indicator_plt.plot(i_macd.diff, pen='y')
macd_items_dict['dea'] = indicator_plt.plot(i_macd.dea, pen='w')
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
# date_slicer.setLimits(xMin=data.timeindex.min(),
#                       xMax=data.timeindex.max(),
#                       yMin=data.close.min(),
#                       yMax=data.close.max())
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

# def ohlc_Xrange_update():


def date_slicer_update():
    # global ohlc_plt, date_slicer
    try:
        ohlc_plt.setXRange(*date_region.getRegion(), padding=0)
    except Exception as e:
        print(e)


date_region.sigRegionChanged.connect(date_slicer_update)
ohlc_plt.sigXRangeChanged.connect(ohlc_Yrange_update)
date_slicer_update()




def update_data_plot():
    global data
    newdata = new_market_data(data)
    print('新数据', newdata.data)
    data.update(newdata)
    ohlcitems.set_data(data)
    for w in ma_items_dict:
        ma_items_dict[w].setData(data.timeindex, getattr(i_ma, w))

    pos_index = i_macd.to_df().macd >= 0
    neg_index = i_macd.to_df().macd < 0
    macd_items_dict['diff'].setData(i_macd.diff)
    macd_items_dict['dea'].setData(i_macd.dea)
    macd_items_dict['macd_pos'].setOpts(x=i_macd.timeindex[pos_index], height=i_macd.macd[pos_index])
    macd_items_dict['macd_neg'].setOpts(x=i_macd.timeindex[neg_index], height=i_macd.macd[neg_index])
    date_slicer.plot(data.timeindex, data.close)
    date_slicer_update()



    # ohlcitems.sigXRangeChanged
    app.processEvents()

timer = QtCore.QTimer()
timer.timeout.connect(update_data_plot)
timer.start(1000)




if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()