#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC  # 导入主图OHLC数据类
from data_fetch.info_data import INFO
from data_handle.indicator import MA, MACD, STD  # 导入指标
from data_handle.spec_handler import MACD_HL_MARK, BuySell
from data_visualize.Login_ui import LoginDialog  # 导入登录界面类
from util import *  # 导入常用函数
from data_fetch.trade_data import TradeData  # 导入交易数据类
from pyqtgraph.Qt import QtCore, QtWidgets
import sys
from data_visualize import MainWindow
from order import OrderDialog
from data_visualize.graph import *
from sp_func.data import init_data_sub, load_product_info, get_product_info

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
info = INFO()
ohlc(daterange=[Start_Time, End_Time])
i_ma = MA(ma10=10, ma20=20, ma30=30, ma60=60)
i_macd = MACD(short=10, long=22, m=9)
i_std = STD(window=60, min_periods=2)
h_macd_hl_mark = MACD_HL_MARK()
h_buysell = BuySell()
trade_datas = TradeData('HSENG$.APR8')
extra_data = [i_ma, i_macd, i_std, h_macd_hl_mark, h_buysell, trade_datas]
# 将指标假如到主图数据里
ohlc.active_ticker()
ohlc.active_price()
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
w_ohlc.init_main_plt()  # 初始化main画布
w_ohlc.init_indicator1_plt()  # 初始化indicator画布
w_ohlc.init_indicator2_plt()  # 初始化indicator2画布
w_ohlc.init_slicer_plt()  # 初始化slicer画布
# 创建图形实例
w_ohlc + Graph_OHLC(w_ohlc.main_plt)
w_ohlc + Graph_MA(w_ohlc.main_plt)
w_ohlc + Graph_MACD(w_ohlc.indicator_plt)
w_ohlc + Graph_MACD_HL_MARK(w_ohlc.main_plt)
w_ohlc + Graph_STD(w_ohlc.indicator2_plt)
w_ohlc + Graph_Trade_Data_Mark(w_ohlc.main_plt)
w_ohlc + Graph_Slicer(w_ohlc.date_slicer_plt)
w_ohlc + Graph_BuySell(w_ohlc.date_slicer_plt)
for g_name in w_ohlc.graphs:
    w_ohlc.init_graph(g_name)
# w_ohlc.init_graph(Graph_BuySell(w_ohlc.main_plt, buy_brush='b', sell_brush='y'))

w_ohlc.init_mouseaction()  # 初始化十字光标与鼠标交互
namespace = {'ohlc': ohlc, 'trade_datas': trade_datas, 'win': win, 'w_ohlc':w_ohlc, 'help_doc': help_doc, 'info': info}  # console的命名空间
w_ohlc.init_console_widget(namespace)  # 初始化交互界面
w_ohlc.init_signal()  # 初始化指标信号
w_ohlc.init_date_region()  # 初始化可视化范围
w_ohlc.ohlc_data_update_sync()  # 主图的横坐标的初始化刷新调整
V_logger.info(f'初始化图表完成')
info.receiver_start()
w_ohlc.chart_replot()
# load_product_info(symbol_list)
# prod_info = get_product_info(symbol_list)
# win.init_main_signal()
win.init_data_signal()
if __name__ == '__main__':

    login_win = LoginDialog()  # 登录界面
    login_win.UserName.setFocus()
    login_win.show()
    login_win.accepted.connect(win.show)
    login_win.rejected.connect(app.closeAllWindows)
    order_dialog = OrderDialog()
    win.pushButton_order.released.connect(order_dialog.show)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())