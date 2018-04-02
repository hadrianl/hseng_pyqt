#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/21 0021 11:49
# @Author  : Hadrianl 
# @File    : OHLC_ui.py
# @reference: uiKLine/uiKLine.py@moonnejs from github.com
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pyqtgraph as pg
from data_visualize.baseitems import DateAxis, CandlestickItem, TradeDataScatter, TradeDataLinkLine
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.Qt import QFont, QBrush, QColor
from util import *
import pandas as pd
from data_visualize.accessory import mouseaction
import numpy as np
import datetime as dt
from functools import partial
from data_visualize.Console_ui import AnalysisConsole
from sp_func.order import *


class KeyEventWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMouseTracking(True)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        if a0.key() == QtCore.Qt.Key_Up:
            self.on_K_Up()
        elif a0.key() == QtCore.Qt.Key_Down:
            self.on_K_Down()
        elif a0.key() == QtCore.Qt.Key_Left:
            self.on_K_Left()
        elif a0.key() == QtCore.Qt.Key_Right:
            self.on_K_Right()

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_RightClick(a0.pos())
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_LeftClick(a0.pos())

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_RightRelease(a0.pos())
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_LeftRelease(a0.pos())

    def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent):
        if a0.button() == QtCore.Qt.RightButton:
            self.on_M_Right_Double_Click()
        elif a0.button() == QtCore.Qt.LeftButton:
            self.on_M_Left_Double_Click()
    # def wheelEvent(self, a0: QtGui.QWheelEvent):
    #     if a0.angleDelta() > 0:
    #         self.on_M_WheelUp()
    #     else:
    #         self.on_M_WheelDown()

    def paintEvent(self, a0: QtGui.QPaintEvent):
        self.onPaint()

    def on_K_Up(self): ...
    def on_K_Down(self): ...
    def on_K_Left(self): ...
    def on_K_Right(self): ...
    def on_M_RightClick(self, pos): ...
    def on_M_LeftClick(self, pos): ...
    def on_M_RightRelease(self, pos): ...
    def on_M_LeftRelease(self, pos): ...
    def on_M_WheelUp(self): ...
    def on_M_WheelDown(self): ...
    def on_M_Right_Double_Click(self): ...
    def on_M_Left_Double_Click(self): ...
    def onPaint(self): ...


class OHlCWidget(KeyEventWidget):

    sig_M_Left_Double_Click = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        self.parent = parent
        super(OHlCWidget, self).__init__(parent)
        self.pw = pg.PlotWidget()
        self.main_layout = pg.GraphicsLayout(border=(100, 100, 100))
        # self.main_layout.setGeometry(QtCore.QRectF(10, 10, 1200, 700))
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.pw.setCentralItem(self.main_layout)
        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(self.pw)
        self.setLayout(self.vb)
        self.xaxis = DateAxis({}, orientation='bottom')
        self.interlines = []
        self.update_func ={}

    def makePI(self, name):  # 生成PlotItem的工厂函数
        # vb = CustomViewBox()
        plotItem = pg.PlotItem(viewBox=pg.ViewBox(), name=name, axisItems={'bottom': self.xaxis})
        plotItem.setMenuEnabled(False)
        # plotItem.setClipToView(True)
        plotItem.hideAxis('left')
        plotItem.showAxis('right')
        plotItem.setDownsampling(mode='peak')
        # # plotItem.setRange(xRange=(0, 1), yRange=(0, 1))
        plotItem.getAxis('right').setWidth(40)
        plotItem.getAxis('right').setStyle(tickFont=QFont("Roman times", 10, QFont.Bold))
        plotItem.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        plotItem.showGrid(True, True)
        plotItem.hideButtons()
        V_logger.info(f'初始化{name}图表')
        return plotItem

    def binddata(self, **data):  # 实现数据与UI界面的绑定
        for k, v in data.items():
            setattr(self, k, v)
            V_logger.info(f'绑定{k}数据到图表')

    def init_ohlc(self):  # 初始化主图OHLC k线
        self.ohlc_plt = self.makePI('ohlc')
        self.ohlc_plt.setMinimumHeight(300)
        self.ohlcitems = CandlestickItem()
        # self.ohlcitems.setHisData(self.ohlc)
        self.ohlc_plt.addItem(self.ohlcitems)
        self.ohlc_plt.setWindowTitle('market data')
        self.ohlc_plt.showGrid(x=True, y=True)
        self.tickitems = CandlestickItem()
        # self.tickitems.setCurData(self.ohlc)
        # self.ohlc.update()
        self.tickitems.mark_line()
        self.ohlc_plt.addItem(self.tickitems)
        self.ohlc_plt.addItem(self.tickitems.hline)
        self.main_layout.addItem(self.ohlc_plt)
        self.main_layout.nextRow()
        self.update_func['ohlc'] = lambda ohlc: self.ohlcitems.setHisData(ohlc)

    def draw_interline(self, ohlc):  # 画出时间分割线
        x = ohlc.x
        dtime = ohlc.datetime
        if self.interlines:
            for item in self.interlines:
                self.ohlc_plt.removeItem(item)
        self.interlines = []
        timedelta = int(ohlc.ktype[:-1])
        for i,v in (dtime - dtime.shift()).iteritems():
            if v > dt.timedelta(minutes=timedelta):
                interline = pg.InfiniteLine(angle=90, pen=pg.mkPen(color='w', width=0.5, dash=[1, 4, 5, 4]))
                interline.setPos(x[i]-0.5)
                self.interlines.append(interline)

        for line in self.interlines:
            self.ohlc_plt.addItem(line)
        V_logger.info(f'标记时间分割线interline')


    def init_ma(self):  # 初始化主图均线ma
        V_logger.info(f'初始化ma图表')
        self.ma_items_dict = {}
        ma_x = range(len(self.ohlc.data))
        for w in self.i_ma._windows:
            self.ma_items_dict[w] = pg.PlotDataItem(pen=pg.mkPen(color=MA_COLORS.get(w, 'w'), width=1))
            self.ohlc_plt.addItem(self.ma_items_dict[w])
        def ma_update(ohlc):
            x=ohlc.x
            for w in self.ma_items_dict:
                self.ma_items_dict[w].setData(x, getattr(self.i_ma, w).values)

        self.update_func['ma'] = ma_update


    def init_macd(self):  # 初始化macd
        self.macd_items_dict = {}
        self.macd_plt = self.makePI('indicator')
        # self.indicator_plt.setXLink('ohlc')
        self.macd_plt.setMaximumHeight(150)
        macd_x = range(len(self.ohlc.data))
        macd_pens = pd.concat([self.ohlc.close > self.ohlc.open, self.i_macd.macd > 0], 1).apply(
            lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map({3: 'r', 2: 'b', 1: 'y', 0: 'g'})
        macd_brushs = [None if (self.i_macd.macd > self.i_macd.macd.shift(1))[i]
                       else v for i, v in macd_pens.iteritems()]
        self.macd_items_dict['Macd'] = pg.BarGraphItem(x=self.ohlc.x, height=self.i_macd.macd,
                                                       width=0.5, pens=macd_pens, brushes=macd_brushs)
        self.macd_plt.addItem(self.macd_items_dict['Macd'])
        self.macd_items_dict['diff'] = pg.PlotDataItem(pen='y')
        self.macd_plt.addItem(self.macd_items_dict['diff'])
        self.macd_items_dict['dea'] = pg.PlotDataItem(pen='w')
        self.macd_plt.addItem(self.macd_items_dict['dea'])
        self.macd_plt.showGrid(x=True, y=True)
        self.macd_plt.hideAxis('bottom')
        self.macd_plt.getViewBox().setXLink(self.ohlc_plt.getViewBox())  # 建立指标图表与主图表的viewbox连接
        self.main_layout.addItem(self.macd_plt)
        self.macd_hl_mark_items_dict = {}
        self.macd_hl_mark_items_dict['high_pos'] = []
        self.macd_hl_mark_items_dict['low_pos'] = []
        self.main_layout.nextRow()
        def macd_update(ohlc):
            x = self.i_macd.x
            diff = self.i_macd.diff
            dea = self.i_macd.dea
            macd = self.i_macd.macd
            self.macd_items_dict['diff'].setData(x, diff.values)
            self.macd_items_dict['dea'].setData(x, dea.values)
            macd_pens = pd.concat(
                [ohlc.close > ohlc.open, macd > 0], 1).apply(
                lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map({3: 'r', 2: 'b', 1: 'y', 0: 'g'})
            macd_brushes = [None if (macd > macd.shift(1))[i]
                            else v for i, v in macd_pens.iteritems()]
            self.macd_items_dict['Macd'].setOpts(x=x, height=macd, pens=macd_pens, brushes=macd_brushes)

        self.update_func['macd'] = macd_update

        def macd_hl_mark_update(ohlc):
            h_macd_hl_mark = ohlc.indicators['macd_hl_mark']
            x=ohlc.x
            for i in self.macd_hl_mark_items_dict['high_pos']:
                self.ohlc_plt.removeItem(i)
            for i in self.macd_hl_mark_items_dict['low_pos']:
                self.ohlc_plt.removeItem(i)
            self.macd_hl_mark_items_dict['high_pos'].clear()
            self.macd_hl_mark_items_dict['low_pos'].clear()
            for k, v in h_macd_hl_mark.high_pos.iteritems():
                textitem = pg.TextItem(html=f'<span style="color:#FF00FF;font-size:9px">{v}<span/>', border=2,
                                       angle=15, anchor=(0, 1))
                textitem.setPos(x[k], v)
                self.ohlc_plt.addItem(textitem)
                self.macd_hl_mark_items_dict['high_pos'].append(textitem)

            for k, v in h_macd_hl_mark.low_pos.iteritems():
                textitem = pg.TextItem(html=f'<span style="color:#7CFC00;font-size:9px">{v}<span/>', border=1,
                                       angle=-15, anchor=(0, 0))
                textitem.setPos(x[k], v)
                self.ohlc_plt.addItem(textitem)
                self.macd_hl_mark_items_dict['low_pos'].append(textitem)

        self.update_func['macd_hl_mark'] = macd_hl_mark_update

    def init_std(self):  # 初始化std图表
        self.std_items_dict = {}
        self.std_plt = self.makePI('std')
        # self.std_plt.setXLink('ohlc')
        self.std_plt.setMaximumHeight(150)
        std_x = range(len(self.ohlc.data))
        std_inc_pens = pd.cut((self.i_std.inc /self.i_std.std).fillna(0), [-np.inf, -2, -1, 1, 2, np.inf],  # 设置画笔颜色
                                 labels=['g', 'y', 'l', 'b', 'r'])
        inc_gt_std = (self.i_std.inc.abs() / self.i_std.std) > 1
        std_inc_brushes = np.where(inc_gt_std, std_inc_pens, None)  # 设置画刷颜色
        self.std_items_dict['inc'] = pg.BarGraphItem(x=self.i_std.x, height=self.i_std.inc,
                                                     width=0.5, pens=std_inc_pens, brushes=std_inc_brushes)
        self.std_plt.addItem(self.std_items_dict['inc'])
        self.std_items_dict['pos_std'] = pg.PlotDataItem(pen='r')
        self.std_plt.addItem(self.std_items_dict['pos_std'])
        self.std_items_dict['neg_std'] = pg.PlotDataItem(pen='g')
        self.std_plt.addItem(self.std_items_dict['neg_std'])
        self.std_plt.hideAxis('bottom')
        self.std_plt.getViewBox().setXLink(self.ohlc_plt.getViewBox())
        self.main_layout.addItem(self.std_plt)
        self.main_layout.nextRow()

        def std_update(ohlc):
            x = ohlc.x
            inc = self.i_std.inc
            std = self.i_std.std
            pos_std = self.i_std.pos_std
            neg_std = self.i_std.neg_std
            std_inc_pens = pd.cut((inc / std).fillna(0), [-np.inf, -2, -1, 1, 2, np.inf],
                                  labels=['g', 'y', 'l', 'b', 'r'])
            inc_gt_std = (inc.abs() / std) > 1
            std_inc_brushes = np.where(inc_gt_std, std_inc_pens, None)
            self.std_items_dict['pos_std'].setData(x, pos_std)
            self.std_items_dict['neg_std'].setData(x, neg_std)
            self.std_items_dict['inc'].setOpts(x=x, height=inc, pens=std_inc_pens, brushes=std_inc_brushes)

        self.update_func['std'] = std_update

    def init_trade_data(self):
        V_logger.info(f'初始化交易数据标记TradeDataScatter及link_line')
        self.tradeitems_dict = {}
        self.tradeitems_dict['open'] = TradeDataScatter()
        self.tradeitems_dict['close'] = TradeDataScatter()
        self.ohlc_plt.addItem(self.tradeitems_dict['open'])
        self.ohlc_plt.addItem(self.tradeitems_dict['close'])
        self.tradeitems_dict['link_line'] = TradeDataLinkLine(pen=pg.mkPen('w', width=1))
        self.tradeitems_dict['info_text'] = pg.TextItem(anchor=(1, 1))
        self.ohlc_plt.addItem(self.tradeitems_dict['link_line'])
        self.ohlc_plt.addItem(self.tradeitems_dict['info_text'])
    # --------------------------------添加交易数据-----------------------------------------------------------------
        def trade_data_update(ohlc):
            x = ohlc.x
            try:
                self.tradeitems_dict['open'].setData(x=x.reindex(self.trade_datas.open.index.floor(ohlc.ktype)),
                                                     y=self.trade_datas['OpenPrice'],
                                                     symbol=['t1' if t == 0 else 't' for t in self.trade_datas['Type']],
                                                     brush=self.trade_datas['Status'].map(
                                                         {2: pg.mkBrush(QBrush(QColor(0, 0, 255))),
                                                          1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                          0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist())
            except Exception as e:
                V_logger.info(f'初始化交易数据标记TradeDataScatter-open失败')
            try:
                self.tradeitems_dict['close'].setData(x=x.reindex(self.trade_datas.close.index.floor(ohlc.ktype)),
                                                      y=self.trade_datas['ClosePrice'],
                                                      symbol=['t' if t == 0 else 't1' for t in self.trade_datas['Type']],
                                                      brush=self.trade_datas['Status'].map(
                                                          {2: pg.mkBrush(QBrush(QColor(255, 255, 0))),
                                                           1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                           0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist())
            except Exception as e:
                V_logger.info(f'初始化交易数据标记TradeDataScatter-open失败')
        # -------------------------------------------------------------------------------------------------------------
        self.update_func['trade_data'] = trade_data_update

        def link_line(a, b):
            if a is self.tradeitems_dict['open']:
                for i, d in enumerate(self.tradeitems_dict['open'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break
            elif a is self.tradeitems_dict['close']:
                for i, d in enumerate(self.tradeitems_dict['close'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break

            open_x = self.tradeitems_dict['open'].data[index][0]
            open_y = self.tradeitems_dict['open'].data[index][1]
            open_symbol = self.tradeitems_dict['open'].data[index][3]  # open_symbol来区别开仓平仓
            if self.trade_datas["Status"].iloc[index] == 2:
                close_x = self.tradeitems_dict['close'].data[index][0]
                close_y = self.tradeitems_dict['close'].data[index][1]
            else:
                close_x = self.tradeitems_dict['close'].data[index][0]
                close_y = self.ohlc._last_tick.Price if self.ohlc._last_tick else self.ohlc.data.iloc[-1]['close']
            profit = round(close_y - open_y, 2) if open_symbol == "t1" else round(open_y - close_y, 2)
            pen_color_type = ((open_symbol == 't1') << 1) + (open_y < close_y)
            pen_color_map_dict = {0: 'r', 1: 'g', 2: 'g', 3: 'r'}
            self.tradeitems_dict['link_line'].setData([[open_x, open_y],
                                                       [close_x, close_y]],
                                                      pen_color_map_dict[pen_color_type])
            self.tradeitems_dict['info_text'].setHtml(f'<span style="color:white">Account:{self.trade_datas["Account_ID"].iloc[index]}<span/><br/>'
                                                      f'<span style="color:blue">Open :{open_y}<span/><br/>'
                                                      f'<span style="color:yellow">Close:{close_y}<span/><br/>'
                                                      f'<span style="color:white">Type  :{"Long" if open_symbol == "t1" else "Short"}<span/><br/>'
                                                      f'<span style="color:{"red" if profit >=0 else "green"}">Profit:{profit}<span/><br/>'
                                                      f'<span style="color:"white">trader:{self.trade_datas["trader_name"].iloc[index]}<span/>')
            self.tradeitems_dict['info_text'].setPos(self.ohlc_plt.getViewBox().viewRange()[0][1],
                                                     self.ohlc_plt.getViewBox().viewRange()[1][0])

        self.tradeitems_dict['open'].sigClicked.connect(link_line)
        self.tradeitems_dict['close'].sigClicked.connect(link_line)

    def init_date_slice(self):  # 初始化时间切片图
        self.date_slicer = self.makePI('date_slicer')
        self.date_slicer.hideAxis('right')
        self.date_slicer.setMaximumHeight(80)
        self.date_slicer.setMouseEnabled(False, False)
        self.close_curve = self.date_slicer.plot(self.ohlc.x, self.ohlc.close)
        self.date_region = pg.LinearRegionItem([1, 100])
        self.date_slicer.addItem(self.date_region)
        self.main_layout.addItem(self.date_slicer)
        self.update_func['data_slice'] = lambda ohlc: self.close_curve.setData(ohlc.x, ohlc.close)

    def init_mouseaction(self):  # 初始化鼠标十字光标动作以及光标所在位置的信息
        V_logger.info(f'初始化mouseaction交互行为')
        self.mouse = mouseaction()
        self.proxy = self.mouse(self.ohlc_plt, self.macd_plt, self.std_plt, self.date_slicer, self.ohlc,
                                i_ma=self.i_ma, i_macd=self.i_macd, i_std=self.i_std)

    def init_console_widget(self, namespace):
        self.console = AnalysisConsole(namespace)
        self.console.update_daterange(self.ohlc.datetime.min(),
                                      self.ohlc.datetime.max())
        S_logger.addHandler(self.console.logging_handler)

    def init_signal(self):  # 信号的连接与绑定
        V_logger.info(f'初始化交互信号绑定')
        self.ohlc_plt.sigXRangeChanged.connect(self.ohlc_Yrange_update)  # 主图X轴变化绑定Y轴更新高度
        self.date_region.sigRegionChanged.connect(self.date_slicer_update)  # 时间切片变化信号绑定调整画图
        self.ohlc.ohlc_sig.connect(self.chart_replot) # K线更新信号绑定更新画图
        self.ohlc.ticker_sig.connect(self.update_data_plot) # ticker更新信号绑定最后的bar的画图

        self.ohlc.resample_sig.connect(self.chart_replot)  # 重采样重画
        self.ohlc.resample_sig.connect(partial(self.readjust_Xrange)) # 重采样调整视图
        # ----------------------重采样信号--------------------------------------
        self.console.RadioButton_min_1.clicked.connect(partial(self.ohlc.set_ktype, '1T'))
        self.console.RadioButton_min_5.clicked.connect(partial(self.ohlc.set_ktype, '5T'))
        self.console.RadioButton_min_10.clicked.connect(partial(self.ohlc.set_ktype, '10T'))
        self.console.RadioButton_min_30.clicked.connect(partial(self.ohlc.set_ktype, '30T'))
        # -----------------------------------------------------------------------
        self.sig_M_Left_Double_Click.connect(self.console.focus) #主图双击信号绑定console弹出
        self.ohlc.ohlc_sig.connect(lambda : self.console.update_daterange(self.ohlc.datetime.min(),
                                                                          self.ohlc.datetime.max()))
        self.console.Button_history.released.connect(lambda : self.goto_history(self.console.DateTimeEdit_start.dateTime(),
                                                                                  self.console.DateTimeEdit_end.dateTime()))  # 绑定历史回顾函数
        self.console.Button_current.released.connect(self.goto_current)  # 绑定回到当前行情
        self.ohlc.ticker_sig.connect(self.console.add_ticker_to_table)  # 绑定ticker数据到ticker列表
        self.ohlc.price_sig.connect(self.console.add_price_to_table)  # 绑定price数据到price列表

        self.console.Button_market_long.released.connect(lambda: add_market_order(self.ohlc.symbol, 'B', self.console.Edit_qty.text()))
        self.console.Button_market_short.released.connect(lambda: add_market_order(self.ohlc.symbol, 'S', self.console.Edit_qty.text()))
        self.console.Button_limit_long.released.connect(lambda: add_limit_order(self.ohlc.symbol, 'B',self.console.Edit_qty.text(), self.console.Edit_limit_price.text()))
        self.console.Button_limit_short.released.connect(lambda: add_limit_order(self.ohlc.symbol, 'S', self.console.Edit_qty.text(), self.console.Edit_limit_price.text()))


    def init_buttons(self):
        self.consolebutton = QtWidgets.QPushButton(text='交互console', parent=self.pw)
        self.consolebutton.setGeometry(QtCore.QRect(10, 250, 75, 23))

    def chart_replot(self):  # 重新画图
        V_logger.info('更新全部图表')
        ohlc = self.ohlc
        for name, func in self.update_func.items():
            func(ohlc)
        self.draw_interline(ohlc)
        self.xaxis.update_tickval(ohlc.timestamp)
        self.ohlc_data_update_sync()

    def ohlc_Yrange_update(self):  # 更新主图和指标图的高度
        ohlc_plt = self.ohlc_plt
        date_region = self.date_region
        ohlc = self.ohlc
        i_macd = self.i_macd
        i_std = self.i_std
        viewrange = ohlc_plt.getViewBox().viewRange()
        date_region.setRegion(viewrange[0])
        try:
            ohlc_plt.setYRange(ohlc.low[ohlc.x.between(*viewrange[0])].min(),
                               ohlc.high[ohlc.x.between(*viewrange[0])].max())
            self.macd_plt.setYRange(min(i_macd.macd[i_macd.x.between(*viewrange[0])].min(),
                                        i_macd.diff[i_macd.x.between(*viewrange[0])].min(),
                                        i_macd.dea[i_macd.x.between(*viewrange[0])].min()),
                                    max(i_macd.macd[i_macd.x.between(*viewrange[0])].max(),
                                             i_macd.diff[i_macd.x.between(*viewrange[0])].max(),
                                             i_macd.dea[i_macd.x.between(*viewrange[0])].max())
                                    )
            self.std_plt.setYRange(min(i_std.inc[i_std.x.between(*viewrange[0])].min(),
                                       i_std.neg_std[i_std.x.between(*viewrange[0])].min()),
                                   max(i_std.inc[i_std.x.between(*viewrange[0])].max(),
                                       i_std.pos_std[i_std.x.between(*viewrange[0])].max()))
            self.date_slicer.setYRange(ohlc.close.min(), ohlc.close.max())
        except Exception as e:
            V_logger.debug(f'图表高度更新错误.')


    def date_slicer_update(self):  # 当时间切片发生变化时触发
        try:
            self.ohlc_plt.setXRange(*self.date_region.getRegion(), padding=0)
        except Exception as e:
            V_logger.debug(f'date_slicer更新错误.')

    def ohlc_data_update_sync(self):  # 主图横坐标变化的实现
        date_region = self.date_region
        ohlc = self.ohlc
        date_region_Max = int(date_region.getRegion()[1])
        date_region_len = int(date_region.getRegion()[1] - date_region.getRegion()[0])
        # print(f'可视区域最大值：{date_region_Max}')
        # print(f'图表timeindex最大值：{ohlc.timeindex.max()}')
        if len(ohlc.data) >= ohlc.bar_size:
            if date_region_Max == ohlc.x.max() + 3:  # 判断最新数据是否是在图表边缘
                date_region.setRegion([ohlc.x.max() + 3 - date_region_len, ohlc.x.max() + 3])
            else:
                date_region.setRegion([date_region_Max - date_region_len - 1, date_region_Max - 1])
        else:
            if date_region_Max == ohlc.x.max() + 3:  # 判断最新数据是否是在图表边缘
                date_region.setRegion([ohlc.x.max() + 4 - date_region_len, ohlc.x.max() + 4])
            else:
                date_region.setRegion([date_region_Max - date_region_len, date_region_Max])
        self.ohlc_Yrange_update()
        self.tradeitems_dict['info_text'].setPos(self.ohlc_plt.getViewBox().viewRange()[0][1],
                                                 self.ohlc_plt.getViewBox().viewRange()[1][0])
        self.ohlc_plt.update()

    def readjust_Xrange(self, left_offset=120, right_offset=3):
        """
        重新调整X轴范围，最右侧的数据为基准，向左向右偏移
        :param left_offset:
        :param right_offset:
        :return:
        """
        self.ohlc_plt.setXRange(self.ohlc.x.max() - left_offset, self.ohlc.x.max() + right_offset)

    def update_data_plot(self, new_ticker):  # 当前K线根据ticker数据的更新
        tickitems = self.tickitems
        # ---------------------------更新数据到图表----------------------------------------------------+
        tickitems.update()
        last_ohlc = self.ohlc.data.iloc[-1]
        tickitems.setCurData(self.ohlc)
        tickitems.update()
        # ---------------------------调整画图界面高度----------------------------------------------------+
        viewrange = self.ohlc_plt.getViewBox().viewRange()
        if last_ohlc.high >= viewrange[1][1] or last_ohlc.low <= viewrange[1][0]:
            self.ohlc_plt.setYRange(min(viewrange[1][0], last_ohlc.low),
                                    max(viewrange[1][1], last_ohlc.high))
        # app.processEvents()

    def goto_history(self, start, end):
        from PyQt5.QtCore import QDateTime
        if isinstance(start, QDateTime):
            start = start.toPyDateTime()
        if isinstance(end, QDateTime):
            end = end.toPyDateTime()
        self.ohlc.inactive_ticker()
        self.ohlc([start, end])
        self.ohlc.update()
        self.chart_replot()

    def goto_current(self):
        if not self.ohlc._OHLC__is_ticker_active:
            start, end = date_range('present', bar_num=680)
            self.ohlc([start, end])
            self.ohlc.active_ticker()
            self.ohlc.update()
            self.chart_replot()

    def on_K_Up(self):  # 键盘up键触发，放大
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length - length//7
        new_xrange = [self.mouse.mousePoint.x() - new_length/2, self.mouse.mousePoint.x() + new_length/2]
        if new_xrange[1] >= self.ohlc.x.max():
            new_xrange = [self.ohlc.x.max() + 4 - new_length, self.ohlc.x.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)

    def on_K_Down(self):  # 键盘down键触发，缩小
        ohlc_xrange = self.ohlc_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length + length//7
        new_xrange = [self.mouse.mousePoint.x() - new_length / 2, self.mouse.mousePoint.x() + new_length / 2]
        if new_xrange[1] >= self.ohlc.x.max():
            new_xrange = [self.ohlc.x.max() + 4 - new_length, self.ohlc.x.max() + 4]
        self.ohlc_plt.setXRange(*new_xrange)

    def on_M_Right_Double_Click(self):  # 鼠标右键双击触发，跳转到当前视图
        self.readjust_Xrange()

    def on_M_Left_Double_Click(self):
        self.sig_M_Left_Double_Click.emit()

