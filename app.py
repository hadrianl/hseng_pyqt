#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 18:46
# @Author  : Hadrianl 
# @File    : app.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from data_fetch.market_data import OHLC, NewOHLC
from data_handle.indicator import Ma, Macd, Std
from data_visualize.OHLC_ui import OHlCWidget
from data_visualize.console import AnalysisConsole
from data_visualize.Login_ui import LoginDialog
from data_fetch.util import MONTH_LETTER_MAPS, print_tick
from data_fetch.trade_data import TradeData
import datetime as dt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import sys


pg.setConfigOptions(leftButtonPan=True, crashWarning=True)
# ------------------------------数据获取与整理---------------------------+
# 确定需要展示的K先范围
start_time = dt.datetime.now() - dt.timedelta(minutes=680)
end_time = dt.datetime.now() + dt.timedelta(minutes=10)
symbol = 'HSI' + MONTH_LETTER_MAPS[dt.datetime.now().month] + str(dt.datetime.now().year)[-1]  # 根据当前时间生成品种代码
# 初始化主图的历史ohlc，最新ohlc与指标数据的参数配置
ohlc = OHLC(start_time, end_time, 'HSIH8', minbar=580)
tick_datas = NewOHLC('HSIH8')
i_macd = Macd(short=10, long=22, m=9)
i_ma = Ma(ma10=10, ma20=20, ma30=30, ma60=60)
i_std = Std(window=60, min_periods=2)
trade_datas = TradeData(start_time, end_time, 'HSENG$.MAR8')
# 将指标假如到主图数据里
ohlc + i_ma
ohlc + i_macd
ohlc + i_std
# -----------------------------------------------------------------------+
# -----------------------窗口与app初始化---------------------------------+
app = QtWidgets.QApplication(sys.argv)
win = OHlCWidget()
win.setWindowTitle(symbol + '实盘分钟图')
# 各个初始化之间存在依赖关系，需要按照以下顺序初始化
win.binddata(ohlc=ohlc, tick_datas=tick_datas, i_ma=i_ma, i_macd=i_macd, i_std=i_std, trade_datas=trade_datas)  # 把数据与UI绑定
win.init_ohlc()  # 初始化ohlc主图
win.init_ma()  # 初始化ma均线图
win.init_macd()  # 初始化指标
win.init_std()  # 初始化std指标
win.init_trade_data()  # 初始化交易数据的对接
win.init_date_slice()  # 初始化时间切片
win.init_mouseaction()  # 初始化十字光标与鼠标交互
win.init_signal()  # 初始化指标
win.tick_datas.active()  # 启动tick_datas
win.date_region.setRegion([win.ohlc.timeindex.max() - 120, win.ohlc.timeindex.max() + 5])  # 初始化可视区域
win.tick_datas._timeindex = ohlc.timeindex.iloc[-1] + 1
win.ohlc_data_update_sync()  # 主图的横坐标的初始化刷新调整
tick_datas.ticker_sig.connect(print_tick)



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


namespace = {'ohlc': ohlc, 'tick_datas': tick_datas, 'trade_datas': trade_datas, 'win': win, 'help_doc': help_doc}  # console的命名空间
console = AnalysisConsole(namespace)


if __name__ == '__main__':
    from login import Ui_LoginWindow
    from PyQt5.Qt import QDialog
    def show():
        if console.isHidden():
            console.show()
        else:
            console.focusWidget()

    win.resize(1200, 800)
    login_win = LoginDialog()
    login_win.UserName.setFocus()
    login_win.show()
    login_win.accepted.connect(win.show)
    login_win.rejected.connect(app.closeAllWindows)
    win.sig_M_Left_Double_Click.connect(show)  # 绑定双击行为调出console
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())