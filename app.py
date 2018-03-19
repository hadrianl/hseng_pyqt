#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC  # 导入主图OHLC数据类
from data_handle.indicator import Ma, Macd, Std  # 导入指标
from data_visualize.OHLC_ui import OHlCWidget  # 导入OHLC可视化类
from data_visualize.console import AnalysisConsole # 导入分析交互界面类
from data_visualize.Login_ui import LoginDialog  # 导入登录界面类
from util import *  # 导入常用函数
from data_fetch.trade_data import TradeData  # 导入交易数据类
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import sys


pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
# 确定需要展示的K线范围
Start_Time, End_Time = date_range('history', start='2018/03/15', bar_num=680)
Symbol = symbol('HSI')
# 初始化主图的历史ohlc，最新ohlc与指标数据的参数配置
ohlc = OHLC(Start_Time, End_Time, 'HSIH8', minbar=580, ktype='5T')
i_macd = Macd(short=10, long=22, m=9)
i_ma = Ma(ma10=10, ma20=20, ma30=30, ma60=60)
i_std = Std(window=60, min_periods=2)
trade_datas = TradeData(Start_Time, End_Time, 'HSENG$.MAR8')
# 将指标假如到主图数据里
ohlc + i_ma
ohlc + i_macd
ohlc + i_std
ohlc.update()
F_logger.info('初始化OHLC数据完成')
# -----------------------------------------------------------------------+
# -----------------------窗口与app初始化---------------------------------+
V_logger.info('初始化app')
app = QtWidgets.QApplication(sys.argv)
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
win.init_signal()  # 初始化指标信号
win.date_region.setRegion([win.ohlc.x.max() - 120, win.ohlc.x.max() + 5])  # 初始化可视区域
win.ohlc.active_ticker()
win.ohlc_data_update_sync()  # 主图的横坐标的初始化刷新调整
V_logger.info(f'初始化ohlc图表完成')



def help_doc():
    text = f'''主要命名空间：ohlc, tick_datas,trade_datas, win
    ohlc是数据类的历史K线数据；tick_datas是数据类的当前K线数据(包括当前k线内的tick数据）；
    trade_datas是交易数据；win是可视化类的主窗口
    主要用法：
    ohlc.data-历史K线数据
    ohlc.indicator-历史K线指标数据
    ohlc.open-历史K线open
    ohlc.high-历史K线high
    ohlc.low-历史K线low
    ohlc.close-历史K线close
    ohlc.datetime-历史K线时间
    ohlc.timestamp-历史K线时间戳
    ohlc.timeindex-历史k线时间序列
    tick_datas有ohlc以上的所有属性，另外
    tick_datas.ticker-当前K线的ticker数据
    trade_datas.account-交易数据包含的账户
    win.ohlc_plt-主窗口主图
    win.indicator_plt-主窗口指标图
    win.ma_items_dict-主窗口ma
    win.macd_items_dict-主窗口macd
    win.std_plt-主窗口std图
    win.std_items_dict-主窗口std
    win.mouse-主窗口鼠标
    '''
    print(text)
    return


namespace = {'ohlc': ohlc, 'trade_datas': trade_datas, 'win': win, 'help_doc': help_doc}  # console的命名空间
console = AnalysisConsole(namespace)


if __name__ == '__main__':

    win.resize(1200, 800)
    login_win = LoginDialog()
    login_win.UserName.setFocus()
    login_win.show()
    login_win.accepted.connect(win.show)
    login_win.rejected.connect(app.closeAllWindows)
    win.sig_M_Left_Double_Click.connect(console.focus)  # 绑定双击行为调出console
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())