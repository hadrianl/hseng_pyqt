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
#------------------------------数据获取与整理---------------------------+
data = market_data('2017-12-12','2017-12-14 21:00:00','HSIc1')
i_macd = macd(short=10, long=22, m=9)
i_ma = ma(ma10=10, ma20=20, ma30=30,ma60=60)
data.indicator_register(i_ma)
data.indicator_register(i_macd)
#-----------------------------------------------------------------------+
#-----------------------窗口与app初始化---------------------------------+
app = QtWidgets.QApplication([])
win = pg.GraphicsWindow()
win.resize(1000,900)
#-----------------------------------------------------------------------+
xaxis = DateAxis(data.timestamp, orientation='bottom')##时间坐标轴
ohlc_plt = win.addPlot(row=0,col=0, axisItems={'bottom': xaxis})    #添加主图表

info_text = pg.TextItem(anchor=(0, 1))
xaxis_text = pg.TextItem(anchor=(1, 1))
yaxis_text = pg.TextItem()
ohlc_plt.addItem(info_text)
ohlc_plt.addItem(xaxis_text)
ohlc_plt.addItem(yaxis_text)
ohlcitems = CandlestickItem()
ohlcitems.setData(data)




ohlc_plt.addItem(ohlcitems)         #向主图表加入k线
ma_items_dict = {}
for w in i_ma._windows:       ##在主图表画出均线
    ma_items_dict[w] = ohlc_plt.plot(data.timeindex, getattr(i_ma, w), pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
# for w in i_ma._windows:
#     ma_items_dict[w] = pg.PlotCurveItem(clickable=True)
#     ma_items_dict[w].setData(data.timeindex.values, getattr(i_ma, w).values, pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
#     ohlc_plt.addItem(ma_items_dict[w])
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
macd_items_dict['diff'] = indicator_plt.plot(i_macd.timeindex, i_macd.diff, pen='y')
macd_items_dict['dea'] = indicator_plt.plot(i_macd.timeindex, i_macd.dea, pen='w')
indicator_plt.showGrid(x=True, y=True)
indicator_plt.hideAxis('bottom')
indicator_plt.getViewBox().setXLink(ohlc_plt.getViewBox())    #建立指标图表与主图表的viewbox连接
#------------------------------------------------------------------+
#---------------添加时间切片图表-----------------------------------+
win.nextRow()
date_slicer = win.addPlot(row=2,col=0)
date_slicer.hideAxis('bottom')
date_slicer.setMouseEnabled(False, False)
close_curve = date_slicer.plot(data.timeindex, data.close)
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
        x_index = {0: data.timeindex.max(), 1: int(mousePoint.x()), 3: data.timeindex.min()}.\
            get(((mousePoint.x() <=  data.timeindex.min())<<1) + (mousePoint.x() <=  data.timeindex.max()))
        try:
            text_df = data.data.iloc[x_index]
            html = f"""
            <span style="color:white">时间:<span/><span style="color:blue">{str(text_df.datetime)[9:16].replace(" ", "日")}<span/><br/>
            <span style="color:white">开盘:<span/><span style="color:red">{text_df.open}<span/><br/>
            <span style="color:white">最高:<span/><span style="color:red">{text_df.high}<span/><br/>
            <span style="color:white">最低:<span/><span style="color:red">{text_df.low}<span/><br/>
            <span style="color:white">收盘:<span/><span style="color:red">{text_df.close}<span/>
            """
            info_text.setPos(x_index, mousePoint.y())
            info_text.setHtml(html)
            xaxis_text.setPos(x_index, ohlc_plt.getViewBox().viewRange()[1][0])
            xaxis_text.setText(str(text_df.datetime))
            yaxis_text.setPos(ohlc_plt.getViewBox().viewRange()[0][0], mousePoint.y())
            yaxis_text.setText('{:.2f}'.format(mousePoint.y()))
        except IndexError as e:
            print(e)
        finally:
            vLine.setPos(x_index)
            hLine.setPos(mousePoint.y())

proxy = pg.SignalProxy(ohlc_plt.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
#------------------------------------------------------------------+

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
        print(e)

def date_slicer_update():
    try:
        ohlc_plt.setXRange(*date_region.getRegion(), padding=0)
    except Exception as e:
        print(e)

def ohlc_data_update_sync():
    date_region_Max = int(date_region.getRegion()[1])
    date_region_len = int(date_region.getRegion()[1] - date_region.getRegion()[0])
    print(date_region_Max)
    print(data.timeindex.max())
    if date_region_Max == data.timeindex.max() + 1:    ##判断最新数据是否是在图表边缘
        date_region.setRegion([data.timeindex.max() + 1 - date_region_len, data.timeindex.max() + 1])
        ohlc_Yrange_update()
    else:
        date_region.setRegion([date_region_Max - date_region_len-1, date_region_Max-1])
    ohlc_plt.update()

def update_data_plot():
    global data, is_lastbar
    newdata = new_market_data(data)
    data.update(newdata)   ##更新新的数据
    #---------------------------更新数据到图表----------------------------------------------------+
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
    #------------------------------------------------------------------------------------------------+
    ohlc_data_update_sync()
    app.processEvents()

date_region.sigRegionChanged.connect(date_slicer_update)
ohlc_plt.sigXRangeChanged.connect(ohlc_Yrange_update)
date_slicer_update()

timer = QtCore.QTimer()
timer.timeout.connect(update_data_plot)
timer.start(1000)




if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QGuiApplication.instance().exec_()