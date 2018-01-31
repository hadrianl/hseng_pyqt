#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC, NewOHLC
from data_handle.indicator import macd, ma
from data_visualize.OHLC_ui import OHlCWidget
import datetime as dt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import sys


pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
start_time = dt.datetime.now() - dt.timedelta(minutes=120)
end_time = dt.datetime.now() + dt.timedelta(minutes=10)
ohlc = OHLC(start_time, end_time, 'HSIG8', minbar=200)
i_macd = macd(short=10, long=22, m=9)
i_ma = ma(ma10=10, ma20=20, ma30=30, ma60=60)
ohlc + i_ma
ohlc + i_macd
tick_datas = NewOHLC('HSIG8')

# -----------------------------------------------------------------------+
# -----------------------窗口与app初始化---------------------------------+
app = QtWidgets.QApplication(sys.argv)
win = OHlCWidget()
  # 各个初始化之间存在依赖关系，需要按照以下方式初始化
win.binddata(ohlc=ohlc,tick_datas=tick_datas, i_ma=i_ma, i_macd=i_macd)
win.init_ohlc()  # 初始化ohlc主图
win.init_ma()  # 初始化ma均线图
win.init_indicator()  # 初始化指标
win.init_date_slice()  # 初始化时间切片
win.init_mouseaction()
win.init_signal()  # 初始化指标

win.tick_datas.active()
win.date_region.setRegion([win.ohlc.timeindex.max() - 120, win.ohlc.timeindex.max() + 5])  # 初始化可视区域
win.tick_datas._timeindex = ohlc.timeindex.iloc[-1] + 1
win.ohlc_data_update_sync()


if __name__ == '__main__':
    win.resize(1200, 800)
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())
