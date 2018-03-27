#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC  # 导入主图OHLC数据类
from data_handle.indicator import Ma, Macd, Std  # 导入指标
from data_handle.spec_handler import MACD_HL_MARK
from data_visualize.OHLC_ui import OHlCWidget  # 导入OHLC可视化类
from data_visualize.Console_ui import AnalysisConsole # 导入分析交互界面类
from data_visualize.Login_ui import LoginDialog  # 导入登录界面类
from util import *  # 导入常用函数
from data_fetch.trade_data import TradeData  # 导入交易数据类
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import sys
from functools import partial


pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
# 确定需要展示的K线范围
Start_Time, End_Time = date_range('present', bar_num=680)
Symbol = symbol('HSI')
# 初始化主图的历史ohlc，最新ohlc与指标数据的参数配置
ohlc = OHLC('HSIH8', minbar=580, ktype='1T')
ohlc(daterange=[Start_Time, End_Time])
i_macd = Macd(short=10, long=22, m=9)
i_ma = Ma(ma10=10, ma20=20, ma30=30, ma60=60)
i_std = Std(window=60, min_periods=2)
h_macd_hl_mark = MACD_HL_MARK()
trade_datas = TradeData('HSENG$.MAR8')
ohlc.active_ticker()
ohlc.active_price()
# 将指标假如到主图数据里
ohlc._thread_lock.acquire()
ohlc + i_ma
ohlc + i_macd
ohlc + h_macd_hl_mark
ohlc + i_std
ohlc + trade_datas
ohlc._thread_lock.release()
F_logger.info('初始化OHLC数据完成')
# -----------------------------------------------------------------------+
# -----------------------app初始化---------------------------------+
V_logger.info('初始化app')
app = QtWidgets.QApplication(sys.argv)
# -----------------------OHLC窗口初始化---------------------------------+
win = OHlCWidget()
win.setWindowTitle(Symbol + '实盘分钟图')
# 各个初始化之间存在依赖关系，需要按照以下顺序初始化
win.binddata(ohlc=ohlc, i_ma=i_ma, i_macd=i_macd, i_std=i_std, trade_datas=trade_datas)  # 把数据与UI绑定
win.init_ohlc()  # 初始化ohlc主图
win.init_ma()  # 初始化ma均线图
win.init_macd()  # 初始化指标
win.init_std()  # 初始化std指标
win.init_trade_data()  # 初始化交易数据的对接
win.init_date_slice()  # 初始化时间切片
win.init_mouseaction()  # 初始化十字光标与鼠标交互
namespace = {'ohlc': ohlc, 'trade_datas': trade_datas, 'win': win, 'help_doc': help_doc}  # console的命名空间
win.init_console_widget(namespace)  # 初始化交互界面
win.init_signal()  # 初始化指标信号
win.date_region.setRegion([win.ohlc.x.max() - 120, win.ohlc.x.max() + 5])  # 初始化可视区域
win.ohlc_data_update_sync()  # 主图的横坐标的初始化刷新调整
V_logger.info(f'初始化ohlc图表完成')
ohlc.active_ticker()
ohlc.active_price()
win.chart_replot()

if __name__ == '__main__':
    win.resize(1200, 800)
    login_win = LoginDialog()
    login_win.UserName.setFocus()
    login_win.show()
    login_win.accepted.connect(win.show)
    login_win.rejected.connect(app.closeAllWindows)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())