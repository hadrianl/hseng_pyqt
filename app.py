#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC  # 导入主图OHLC数据类
from data_fetch.info_data import INFO
from data_handle.indicator import MA, MACD, STD  # 导入指标
from data_handle.spec_handler import MACD_HL_MARK, BuySell, COINCIDE
from util import *  # 导入常用函数
from data_fetch.trade_data import TradeData  # 导入交易数据类
from pyqtgraph.Qt import QtCore, QtWidgets
from PyQt5.QtCore import Qt
import sys
from data_visualize import MainWindow
from data_visualize.graph import *
import experimental as test

V_logger.info('初始化app')
pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
# 确定需要展示的K线范围
Start_Time, End_Time = date_range('present', bar_num=680)
Symbol = symbol('HSI')
symbol_list = ['HSIJ8']
# init_data_sub(symbol_list)
# 初始化主图的历史ohlc，最新ohlc与指标数据的参数配置
ohlc = OHLC('HSIJ8',minbar=600, ktype='1T')
ohlc(daterange=[Start_Time, End_Time])
i_ma = MA(ma10=10, ma20=20, ma30=30, ma60=60)
i_macd = MACD(short=10, long=22, m=9)
i_std = STD(window=60, min_periods=2)
h_macd_hl_mark = MACD_HL_MARK()
i_coincide=COINCIDE()
h_buysell = BuySell()
trade_datas = TradeData('HSENG$.APR8')
extra_data = [i_ma, i_macd, i_std, h_macd_hl_mark, h_buysell,i_coincide, trade_datas]
# 将指标假如到主图数据里
ohlc.active_ticker()  # 让ticker数据推送生效
ohlc.active_price()  #让price数据推送生效
ohlc._thread_lock.acquire()
for d in extra_data:
    ohlc + d
ohlc._thread_lock.release()
F_logger.info('初始化OHLC数据完成')
# -----------------------------------------------------------------------+
# -----------------------app初始化---------------------------------+

app = QtWidgets.QApplication(sys.argv)
# -----------------------OHLC窗口初始化---------------------------------+
win = MainWindow()
w_ohlc = win.QWidget_ohlc
win.setWindowTitle(Symbol + '实盘分钟图')
# 各个初始化之间存在上下文依赖关系，需要按照以下顺序初始化
w_ohlc.binddata(ohlc)  # 把数据与UI绑定
w_ohlc.init_plt()  # 初始化画布并绑定了初始化与反初始化函数在字典plt_init_func与plt_deinit_func中
# 创建图形实例
w_ohlc + Graph_OHLC([w_ohlc.plts['main'], w_ohlc.plts['indicator3']])
w_ohlc + Graph_MA([w_ohlc.plts['main']])
w_ohlc + Graph_MACD([w_ohlc.plts['indicator1']])
w_ohlc + Graph_MACD_HL_MARK([w_ohlc.plts['main']])
w_ohlc + Graph_STD([w_ohlc.plts['indicator2']])
w_ohlc + Graph_Trade_Data_Mark([w_ohlc.plts['main']])
w_ohlc + Graph_COINCIDE([w_ohlc.plts['main']])
w_ohlc + Graph_Slicer([w_ohlc.plts['date_slicer']])
w_ohlc + Graph_BuySell([w_ohlc.plts['date_slicer']])
for g_name in w_ohlc.graphs:
    w_ohlc.init_graph(g_name)

w_ohlc.init_mouseaction()  # 初始化十字光标与鼠标交互
namespace = {'ohlc': ohlc, 'trade_datas': trade_datas, 'win': win, 'w_ohlc':w_ohlc, 'help_doc': help_doc, 'test': test}  # console的命名空间
w_ohlc.init_console_widget(namespace)  # 初始化交互界面
w_ohlc.init_signal()  # 初始化指标信号
win.init_signal()
win.init_test()


# 完成初始化的视图调整
w_ohlc.init_date_region()  # 初始化可视化范围
V_logger.info(f'初始化图表完成')
# win.init_login_win()


if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec_())