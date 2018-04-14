#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/21 0021 11:49
# @Author  : Hadrianl 
# @File    : OHLC_ui.py
# @reference: uiKLine/uiKLine.py@moonnejs from github.com
# @License : (C) Copyright 2013-2017, 凯瑞投资


from data_visualize.baseitems import DateAxis
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.Qt import QFont
from util import *
from data_visualize.accessory import mouseaction
import datetime as dt
from functools import partial
from data_visualize.Console_ui import AnalysisConsole
from PyQt5.QtWidgets import QDesktopWidget
from order import OrderDialog
from sp_func.order import *
from data_visualize.graph import *


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
        self.susp = Suspended_Widget()
        self.main_layout = pg.GraphicsLayout(border=(100, 100, 100))
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.pw.setCentralItem(self.main_layout)
        self.vb = QtWidgets.QVBoxLayout()
        self.vb.addWidget(self.pw)
        self.setLayout(self.vb)
        self.xaxis = DateAxis({}, orientation='bottom')
        self.interlines = []
        self.plt_init_func = {}
        self.plt_deinit_func = {}
        self.graphs = {}


    def makePI(self, name):  # 生成PlotItem的工厂函数
        # vb = CustomViewBox()
        plotItem = pg.PlotItem(viewBox=pg.ViewBox(), name=name, axisItems={'bottom': self.xaxis})
        plotItem.setMenuEnabled(False)
        # plotItem.setClipToView(True)
        plotItem.hideAxis('left')
        plotItem.showAxis('right')
        plotItem.setDownsampling(mode='peak')
        # # plotItem.setRange(xRange=(0, 1), yRange=(0, 1))
        plotItem.getAxis('right').setWidth(30)
        plotItem.getAxis('right').setStyle(tickFont=QFont("Roman times", 6, QFont.Bold))
        plotItem.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        plotItem.showGrid(True, True)
        plotItem.hideButtons()
        V_logger.info(f'初始化{name}画布')
        return plotItem

    def __add__(self, graph):
        self.graphs[graph.name] = graph
        V_logger.info(f'加入{graph.name}图表')

    def __sub__(self, graph):
        if isinstance(graph, graph_base):
            if self.graphs.pop(graph.name, None):
                V_logger.info(f'删除{graph.name}图表')
        elif isinstance(graph, str):
            if self.graphs.pop(graph, None):
                V_logger.info(f'删除{graph}图表')


    def binddata(self, ohlc):  # 实现数据与UI界面的绑定
        self.data = {}
        self.data['ohlc'] = ohlc
        V_logger.info(f'绑定数据到图表')
    # ---------------------------画布初始化与反初始化函数绑定--------------------------
    def init_plt(self):
        def init_main_plt():  # 初始化主图
            self.main_plt = self.makePI('main')
            self.main_plt.setMinimumHeight(300)
            self.main_plt.setWindowTitle('market data')
            self.main_layout.addItem(self.main_plt, 0, 0)
            self.main_layout.nextRow()

        def deinit_main_plt():
            self.main_layout.removeItem(self.main_plt)

        self.plt_init_func['main'] = init_main_plt
        self.plt_deinit_func['main'] = deinit_main_plt

        def init_indicator1_plt():  # 初始化第一个指标图表
            self.indicator1_plt = self.makePI('indicator1')
            self.indicator1_plt.setMaximumHeight(150)
            self.main_layout.addItem(self.indicator1_plt, 1, 0)
            self.indicator1_plt.hideAxis('bottom')
            self.indicator1_plt.getViewBox().setXLink(self.main_plt.getViewBox())  # 建立指标图表与主图表的viewbox连接
            self.main_layout.nextRow()

        def deinit_indicator1_plt():
            self.main_layout.removeItem(self.indicator1_plt)

        self.plt_init_func['indicator1'] = init_indicator1_plt
        self.plt_deinit_func['indicator1'] = deinit_indicator1_plt

        def init_indicator2_plt():  # 初始化第二个指标图表
            self.indicator2_plt = self.makePI('indicator2')
            self.indicator2_plt.hideAxis('bottom')
            self.indicator2_plt.getViewBox().setXLink(self.main_plt.getViewBox())
            self.main_layout.addItem(self.indicator2_plt, 2, 0)
            self.main_layout.nextRow()

        def deinit_indicator2_plt():
            self.main_layout.removeItem(self.indicator2_plt)

        self.plt_init_func['indicator2'] = init_indicator2_plt
        self.plt_deinit_func['indicator2'] = deinit_indicator2_plt

        def init_indicator3_plt():  # 初始化第三个指标图表
            self.indicator3_plt = self.makePI('indicator3')
            self.indicator3_plt.getViewBox().setXLink(self.main_plt.getViewBox())
            self.susp._layout.addItem(self.indicator3_plt)

        def deinit_indicator3_plt():
            self.susp._layout.removeItem(self.indicator3_plt)

        self.plt_init_func['indicator3'] = init_indicator3_plt
        self.plt_deinit_func['indicator3'] = deinit_indicator3_plt

        def init_slicer_plt():
            self.date_slicer_plt = self.makePI('date_slicer')
            self.date_slicer_plt.hideAxis('right')
            self.date_slicer_plt.setMaximumHeight(80)
            self.date_slicer_plt.setMouseEnabled(False, False)
            self.main_layout.addItem(self.date_slicer_plt, 3, 0)

        def deinit_slicer_plt():
            self.main_layout.removeItem(self.date_slicer_plt)

        self.plt_init_func['date_slicer'] = init_slicer_plt
        self.plt_deinit_func['date_slicer'] = deinit_slicer_plt

        for name in self.plt_init_func:
            self.plt_init_func[name]()
    # --------------------------------------------------------------------------------------------------

    # ---------------------------图表graph初始化，更新，反初始化三连发-------------------------------------
    def init_graph(self,graph_name):
        if graph_name in self.graphs:
            self.graphs[graph_name].init(self.data['ohlc'])

    def update_graph(self, graph_name):
        if graph_name in self.graphs:
            self.graphs[graph_name].update(self.data['ohlc'])

    def deinit_graph(self, graph_name):
        if graph_name in self.graphs:
            self.graphs[graph_name].deinit()
    # ----------------------------------------------------------------------------------------------------

    def draw_interline(self, ohlc):  # 画出时间分割线
        x = ohlc.x
        dtime = ohlc.datetime
        if self.interlines:
            for item in self.interlines:
                self.main_plt.removeItem(item)
        self.interlines = []
        timedelta = int(ohlc.ktype[:-1])
        for i,v in (dtime - dtime.shift()).iteritems():
            if v > dt.timedelta(minutes=timedelta):
                interline = pg.InfiniteLine(angle=90, pen=pg.mkPen(color='w', width=0.5, dash=[1, 4, 5, 4]))
                interline.setPos(x[i]-0.5)
                self.interlines.append(interline)

        for line in self.interlines:
            self.main_plt.addItem(line)
        V_logger.info(f'标记时间分割线interline')


    def init_date_region(self):  # 初始化时间切片图
        ohlc = self.data['ohlc']
        self.graphs['Slicer'].plt_items['date_slicer']['date_region'].setRegion([ohlc.x.max() - 120,
                                                                                 ohlc.x.max() + 5])  # 初始化可视区域
        self.ohlc_Xrange_update()

    def init_mouseaction(self):  # 初始化鼠标十字光标动作以及光标所在位置的信息
        V_logger.info(f'初始化mouseaction交互行为')
        self.mouse = mouseaction()
        ohlc = self.data['ohlc']
        self.proxy = self.mouse(self.main_plt, self.indicator1_plt, self.indicator2_plt, self.date_slicer_plt, ohlc, self.graphs)

    def init_console_widget(self, namespace):
        ohlc = self.data['ohlc']
        self.console = AnalysisConsole(namespace)
        self.console.update_daterange(ohlc.datetime.min(),
                                      ohlc.datetime.max())
        S_logger.addHandler(self.console.logging_handler)  # 加入日志输出到console

    def init_signal(self):  # 信号的连接与绑定
        V_logger.info(f'初始化交互信号绑定')
        ohlc = self.data['ohlc']
        self.main_plt.sigXRangeChanged.connect(self.ohlc_Yrange_update)  # 主图X轴变化绑定Y轴更新高度
        self.graphs['Slicer'].plt_items['date_slicer']['date_region'].sigRegionChanged.connect(self.date_slicer_update)  # 时间切片变化信号绑定调整画图
        ohlc.ohlc_sig.connect(self.chart_replot) # K线更新信号绑定更新画图
        ohlc.ticker_sig.connect(self.tick_update_plot) # ticker更新信号绑定最后的bar的画图
        # ----------------------重采样信号--------------------------------------
        ohlc.resample_sig.connect(self.chart_replot)  # 重采样重画
        ohlc.resample_sig.connect(partial(self.readjust_Xrange)) # 重采样调整视图
        self.console.RadioButton_min_1.clicked.connect(partial(ohlc.set_ktype, '1T'))
        self.console.RadioButton_min_5.clicked.connect(partial(ohlc.set_ktype, '5T'))
        self.console.RadioButton_min_10.clicked.connect(partial(ohlc.set_ktype, '10T'))
        self.console.RadioButton_min_30.clicked.connect(partial(ohlc.set_ktype, '30T'))
        # -----------------------------------------------------------------------
        self.sig_M_Left_Double_Click.connect(self.console.focus) #主图双击信号绑定console弹出
        ohlc.ohlc_sig.connect(lambda : self.console.update_daterange(ohlc.datetime.min(),
                                                                     ohlc.datetime.max()))
        self.console.Button_history.released.connect(lambda : self.goto_history(self.console.DateTimeEdit_start.dateTime(),
                                                                                self.console.DateTimeEdit_end.dateTime()))  # 绑定历史回顾函数
        self.console.Button_current.released.connect(self.goto_current)  # 绑定回到当前行情
        ohlc.ticker_sig.connect(self.console.add_ticker_to_table)  # 绑定ticker数据到ticker列表
        ohlc.price_sig.connect(self.console.add_price_to_table)  # 绑定price数据到price列表


    # def init_buttons(self):
    #     self.consolebutton = QtWidgets.QPushButton(text='交互console', parent=self.pw)
    #     self.consolebutton.setGeometry(QtCore.QRect(10, 250, 75, 23))

    def chart_replot(self):  # 重新画图
        V_logger.info('G↑更新图表......')
        ohlc = self.data['ohlc']
        for name, graph in self.graphs.items():
            graph.update(ohlc)
        self.draw_interline(ohlc)
        self.xaxis.update_tickval(ohlc.timestamp)
        self.ohlc_Xrange_update()
        V_logger.info('G↑更新图表完成......')

    def ohlc_Yrange_update(self):  # 更新主图和指标图的高度
        date_region = self.graphs['Slicer'].plt_items['date_slicer']['date_region']
        ohlc = self.data['ohlc']
        i_macd = getattr(ohlc, 'MACD', None)
        i_std = getattr(ohlc, 'STD', None)
        viewrange = self.main_plt.getViewBox().viewRange()
        date_region.setRegion(viewrange[0])
        try:
            x_range = ohlc.x.between(*viewrange[0])
            self.main_plt.setYRange(ohlc.low[x_range].min(),ohlc.high[x_range].max())
            self.indicator3_plt.setYRange(ohlc.low[x_range].min(),ohlc.high[x_range].max())
            if getattr(i_macd, 'is_active', None):
                self.indicator1_plt.setYRange(min(i_macd.macd[x_range].min(),
                                                  i_macd.diff[x_range].min(),
                                                  i_macd.dea[x_range].min()),
                                              max(i_macd.macd[x_range].max(),
                                                 i_macd.diff[x_range].max(),
                                                 i_macd.dea[x_range].max())
                                              )
                # self.indicator3_plt.setYRange(min(i_macd.macd[x_range].min(),
                #                                   i_macd.diff[x_range].min(),
                #                                   i_macd.dea[x_range].min()),
                #                               max(i_macd.macd[x_range].max(),
                #                                  i_macd.diff[x_range].max(),
                #                                  i_macd.dea[x_range].max())
                #                               )
            if getattr(i_std, 'is_active', None):
                self.indicator2_plt.setYRange(min(i_std.inc[x_range].min(),
                                                  i_std.neg_std[x_range].min()),
                                              max(i_std.inc[x_range].max(),
                                                  i_std.pos_std[x_range].max())
                                              )
            self.date_slicer_plt.setYRange(ohlc.close.min(), ohlc.close.max())
        except Exception as e:
            V_logger.debug(f'图表高度更新错误.')


    def date_slicer_update(self):  # 当时间切片发生变化时触发
        try:
            date_region = self.graphs['Slicer'].plt_items['date_slicer']['date_region']
            self.main_plt.setXRange(*date_region.getRegion(), padding=0)
        except Exception as e:
            V_logger.debug(f'date_slicer更新错误.')

    def ohlc_Xrange_update(self):  # 主图横坐标变化的实现
        date_region = self.graphs['Slicer'].plt_items['date_slicer']['date_region']
        ohlc = self.data['ohlc']
        date_region_Max = int(date_region.getRegion()[1])
        date_region_len = int(date_region.getRegion()[1] - date_region.getRegion()[0])

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
        self.xaxis.update_tickval(ohlc.timestamp)
        if 'Trade_Data' in self.graphs:
            for p in self.graphs['Trade_Data'].plts:
                text = self.graphs['Trade_Data'].plt_texts[p]
                plt = self.graphs['Trade_Data'].plts[p]
                vbr = plt.getViewBox().viewRange()
                text.setPos(vbr[0][1], vbr[1][0])
        self.main_plt.update()

    def readjust_Xrange(self, left_offset=120, right_offset=3):
        """
        重新调整X轴范围，最右侧的数据为基准，向左向右偏移
        :param left_offset:
        :param right_offset:
        :return:
        """
        x = self.data['ohlc'].x
        self.main_plt.setXRange(x.max() - left_offset, x.max() + right_offset)

    def tick_update_plot(self, new_ticker):  # 当前K线根据ticker数据的更新
        tickitems = self.graphs['OHLC'].items_dict['tick']
        # ---------------------------更新数据到图表----------------------------------------------------+
        tickitems.update()
        ohlc = self.data['ohlc']
        last_ohlc = ohlc.data.iloc[-1]
        tickitems.setCurData(ohlc)
        tickitems.update()
        # ---------------------------调整画图界面高度----------------------------------------------------+
        vbr = self.main_plt.getViewBox().viewRange()
        if last_ohlc.high >= vbr[1][1] or last_ohlc.low <= vbr[1][0]:
            self.main_plt.setYRange(min(vbr[1][0], last_ohlc.low),
                                    max(vbr[1][1], last_ohlc.high))
        # app.processEvents()

    def goto_history(self, start, end):
        V_logger.info(f'回顾历史行情')
        ohlc = self.data['ohlc']
        from PyQt5.QtCore import QDateTime
        if isinstance(start, QDateTime):
            start = start.toPyDateTime()
        if isinstance(end, QDateTime):
            end = end.toPyDateTime()
        ohlc.inactive_ticker()
        ohlc([start, end], False)
        ohlc.update()
        self.chart_replot()

    def goto_current(self):
        V_logger.info(f'回到当前行情')
        ohlc = self.data['ohlc']
        if not ohlc._OHLC__is_ticker_active:
            start, end = date_range('present', bar_num=680)
            ohlc([start, end])
            ohlc.active_ticker()
            ohlc.update()
            self.chart_replot()
            self.init_date_region()

    def on_K_Up(self):  # 键盘up键触发，放大
        ohlc_xrange = self.main_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length - length//7
        x = self.data['ohlc'].x
        new_xrange = [self.mouse.mousePoint.x() - new_length/2, self.mouse.mousePoint.x() + new_length/2]
        if new_xrange[1] >= x.max():
            new_xrange = [x.max() + 4 - new_length, x.max() + 4]
        self.main_plt.setXRange(*new_xrange)

    def on_K_Down(self):  # 键盘down键触发，缩小
        ohlc_xrange = self.main_plt.getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length + length//7
        x = self.data['ohlc'].x
        new_xrange = [self.mouse.mousePoint.x() - new_length / 2, self.mouse.mousePoint.x() + new_length / 2]
        if new_xrange[1] >= x.max():
            new_xrange = [x.max() + 4 - new_length, x.max() + 4]
        self.main_plt.setXRange(*new_xrange)

    def on_M_Right_Double_Click(self):  # 鼠标右键双击触发，跳转到当前视图
        self.readjust_Xrange()

    def on_M_Left_Double_Click(self):
        self.sig_M_Left_Double_Click.emit()


class Suspended_Widget(pg.PlotWidget):
    _startPos = None
    _endPos = None
    _isTracking = False

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.resize(QSize(500, 300))
        desktop = QDesktopWidget()
        desktop_with = desktop.availableGeometry().width()
        self.move(desktop_with - self.width(), 0)
        self._layout = pg.GraphicsLayout(border=(100, 100, 100))
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(0)
        self._layout.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.setCentralItem(self._layout)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)  # 无边框
        self.setWindowOpacity(0.5)


    def mouseMoveEvent(self, e: QMouseEvent):  # 重写移动事件
        if self._isTracking:
            self._endPos = e.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._isTracking = False
            self._startPos = None
            self._endPos = None