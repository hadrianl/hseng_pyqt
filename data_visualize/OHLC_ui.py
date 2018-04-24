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
from PyQt5.Qt import QFont, QIcon, QMenu, QAction
from util import *
from data_visualize.accessory import mouseaction
import datetime as dt
from functools import partial
from data_visualize.Console_ui import AnalysisConsole
from PyQt5.QtWidgets import QDesktopWidget, QApplication
from SpInfo_ui import OrderDialog
from sp_func.local import *
from data_visualize.graph import *
from data_visualize.plt import *
from logging import Handler, Formatter
import re

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
        self.susp.setWindowTitle('悬浮窗口')
        # self.susp.hide()
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
        self.plts = {}
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
        self.plts['main'] = MainPlt('main', self.xaxis)
        self.plts['indicator1'] = IndicatorPlt('indicator1', self.xaxis, (150, 300))
        self.plts['indicator2'] = IndicatorPlt('indicator2', self.xaxis, (150,  300))
        self.plts['indicator3'] = IndicatorPlt('indicator3', self.xaxis)
        self.plts['date_slicer'] = SlicerPlt('date_slicer', self.xaxis)
        self.plts['main'].bind(self.main_layout, 0, 0)
        self.plts['indicator1'].bind(self.main_layout, 1, 0)
        self.plts['indicator2'].bind(self.main_layout, 2, 0)
        self.plts['date_slicer'].bind(self.main_layout, 3, 0)
        self.plts['indicator3'].bind(self.susp._layout)
        self.plts['indicator1'].getViewBox().setXLink(self.plts['main'].getViewBox())
        self.plts['indicator2'].getViewBox().setXLink(self.plts['main'].getViewBox())
        self.plts['indicator3'].getViewBox().setXLink(self.plts['main'].getViewBox())

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
                self.plts['main'].removeItem(item)
        self.interlines = []
        timedelta = int(ohlc.ktype[:-1])
        for i,v in (dtime - dtime.shift()).iteritems():
            if v > dt.timedelta(minutes=timedelta):
                interline = pg.InfiniteLine(angle=90, pen=pg.mkPen(color='w', width=0.5, dash=[1, 4, 5, 4]))
                interline.setPos(x[i]-0.5)
                self.interlines.append(interline)

        for line in self.interlines:
            self.plts['main'].addItem(line)
        V_logger.info(f'标记时间分割线interline')


    def init_date_region(self):  # 初始化时间切片图
        ohlc = self.data['ohlc']
        self.graphs['Slicer'].plt_items['date_slicer']['date_region'].setRegion([ohlc.x.max() - 120,
                                                                                 ohlc.x.max() + 5])  # 初始化可视区域
        ohlc.ohlc_sig.emit()
        ohlc.update()
        self.ohlc_Xrange_update()

    def init_mouseaction(self):  # 初始化鼠标十字光标动作以及光标所在位置的信息
        V_logger.info(f'初始化mouseaction交互行为')
        self.mouse = mouseaction()
        ohlc = self.data['ohlc']
        self.proxy = self.mouse(self.plts, ohlc, self.graphs)

    def init_console_widget(self, namespace):
        ohlc = self.data['ohlc']
        self.console = AnalysisConsole(namespace)
        self.console.update_daterange(ohlc.datetime.min(),
                                      ohlc.datetime.max())
        S_logger.addHandler(self.console.logging_handler)  # 加入日志输出到console

    def init_signal(self):  # 信号的连接与绑定
        V_logger.info(f'初始化交互信号绑定')
        ohlc = self.data['ohlc']
        self.plts['main'].sigXRangeChanged.connect(self.ohlc_Yrange_update)  # 主图X轴变化绑定Y轴更新高度
        self.graphs['Slicer'].plt_items['date_slicer']['date_region'].sigRegionChanged.connect(self.date_slicer_update)  # 时间切片变化信号绑定调整画图
        ohlc.ticker_sig.connect(self.tick_update_plot) # ticker更新信号绑定最后的bar的画图
        # ---------------------------数据更新的信号与图形更新槽连接------------------------------------------------
        ohlc.ohlc_sig.connect(lambda :self.mouse.update(ohlc))
        ohlc.ohlc_sig.connect(lambda :self.graphs['OHLC'].update(ohlc))
        ohlc.ohlc_sig.connect(lambda :self.graphs['Slicer'].update(ohlc))
        for k, v in ohlc.extra_data.items():
            if k in self.graphs:
                v.update_thread.finished.connect(partial(lambda n: self.graphs[n].update(ohlc), k))

        ohlc.ohlc_sig.connect(lambda : self.draw_interline(ohlc))
        ohlc.ohlc_sig.connect(lambda : self.xaxis.update_tickval(ohlc.timestamp))
        ohlc.ohlc_sig.connect(lambda : self.ohlc_Xrange_update())
        ohlc.ohlc_sig.connect(lambda : (plt.update() for _,plt in self.plts.items()))
        # ------------------------------------------------------------------------------------------------------
        # ----------------------重采样信号--------------------------------------
        ohlc.resample_sig.connect(ohlc.ohlc_sig)
        ohlc.resample_sig.connect(partial(self.readjust_Xrange))
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


    def ohlc_Yrange_update(self):  # 更新主图和指标图的高度
        date_region = self.graphs['Slicer'].plt_items['date_slicer']['date_region']
        ohlc = self.data['ohlc']
        i_macd = getattr(ohlc, 'MACD', None)
        i_std = getattr(ohlc, 'STD', None)
        viewrange = self.plts['main'].getViewBox().viewRange()
        date_region.setRegion(viewrange[0])
        try:
            x_range = ohlc.x.between(*viewrange[0])
            self.plts['main'].setYRange(ohlc.low[x_range].min(),ohlc.high[x_range].max())
            self.plts['indicator3'].setYRange(ohlc.low[x_range].min(),ohlc.high[x_range].max())
            if getattr(i_macd, 'is_active', None):
                self.plts['indicator1'].setYRange(min(i_macd.macd[x_range].min(),
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
                self.plts['indicator2'].setYRange(min(i_std.inc[x_range].min(),
                                                  i_std.neg_std[x_range].min()),
                                              max(i_std.inc[x_range].max(),
                                                  i_std.pos_std[x_range].max())
                                              )
                self.plts['date_slicer'].setYRange(ohlc.close.min(), ohlc.close.max())
        except Exception as e:
            V_logger.debug(f'图表高度更新错误.')


    def date_slicer_update(self):  # 当时间切片发生变化时触发
        try:
            date_region = self.graphs['Slicer'].plt_items['date_slicer']['date_region']
            self.plts['main'].setXRange(*date_region.getRegion(), padding=0)
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
        self.plts['main'].update()

    def readjust_Xrange(self, left_offset=120, right_offset=3):
        """
        重新调整X轴范围，最右侧的数据为基准，向左向右偏移
        :param left_offset:
        :param right_offset:
        :return:
        """
        x = self.data['ohlc'].x
        self.plts['main'].setXRange(x.max() - left_offset, x.max() + right_offset)

    def tick_update_plot(self, new_ticker):  # 当前K线根据ticker数据的更新
        plts = self.graphs['OHLC'].plts
        plt_items = self.graphs['OHLC'].plt_items
        ohlc = self.data['ohlc']
        last_ohlc = ohlc.data.iloc[-1]
        for p in plt_items:
            tickitem = plt_items[p]['tick']
            # ---------------------------更新数据到图表----------------------------------------------------+
            tickitem.setCurData(ohlc)
            # ---------------------------调整画图界面高度----------------------------------------------------+
            vbr = plts[p].getViewBox().viewRange()
            if last_ohlc.high >= vbr[1][1] or last_ohlc.low <= vbr[1][0]:
                plts[p].setYRange(min(vbr[1][0], last_ohlc.low),
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
        ohlc.ohlc_sig.emit()
        ohlc.update()


    def goto_current(self):
        V_logger.info(f'回到当前行情')
        ohlc = self.data['ohlc']
        if not ohlc._OHLC__is_ticker_active:
            start, end = date_range('present', bar_num=680)
            ohlc([start, end])
            ohlc.active_ticker()
            ohlc.ohlc_sig.emit()
            ohlc.update()



    def on_K_Up(self):  # 键盘up键触发，放大
        ohlc_xrange = self.plts['main'].getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length - length//7
        x = self.data['ohlc'].x
        new_xrange = [self.mouse.mousePoint.x() - new_length/2, self.mouse.mousePoint.x() + new_length/2]
        if new_xrange[1] >= x.max():
            new_xrange = [x.max() + 4 - new_length, x.max() + 4]
        self.plts['main'].setXRange(*new_xrange)

    def on_K_Down(self):  # 键盘down键触发，缩小
        ohlc_xrange = self.plts['main'].getViewBox().viewRange()[0]
        length = ohlc_xrange[1] - ohlc_xrange[0]
        new_length = length + length//7
        x = self.data['ohlc'].x
        new_xrange = [self.mouse.mousePoint.x() - new_length / 2, self.mouse.mousePoint.x() + new_length / 2]
        if new_xrange[1] >= x.max():
            new_xrange = [x.max() + 4 - new_length, x.max() + 4]
        self.plts['main'].setXRange(*new_xrange)

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


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.push_msg_type = ['<API>']
        self.messager = self.system_message_handler(self)
        self.init_Menu()
        self.init_icon()

    def init_Menu(self):
        self.menu = QMenu()
        self.action_win = QAction("实盘图表", self)
        self.action_susp = QAction('悬浮窗',self)
        self.action_quit = QAction("退出", self)
        # self.menu1 = QMenu()
        # self.menu1.addAction(self.showAction1)
        # self.menu1.addAction(self.showAction2)
        # self.menu.addMenu(self.menu1, )
        # self.menu1.setTitle("二级菜单")
        self.menu.addAction(self.action_win)
        self.menu.addAction(self.action_susp)
        self.menu.addAction(self.action_quit)
        self.setContextMenu(self.menu)

    def init_icon(self):
        # self.activated.connect(self.iconClied)
        # #把鼠标点击图标的信号和槽连接
        # self.messageClicked.connect(self.mClied)
        # #把鼠标点击弹出消息的信号和槽连接
        self.setIcon(QIcon(os.path.join('ui', 'tracking.png')))
        self.icon = self.MessageIcon()
        #设置图标

    def iconClied(self, reason):
        "鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击"
        if reason == 2 or reason == 3:
            pw = self.parent()
            if pw.isVisible():
                pw.hide()
            else:
                pw.show()
        print(reason)

    def mClied(self):
        print(22222)
        self.showMessage("提示", "你点了消息", self.icon)

    def showM(self):
        print(1111)
        self.showMessage("测试", "我是消息", self.icon)
    def aaa(self):
        print('sfsdfsf')

    def push_message(self, info_type, info):
        if info_type in self.push_msg_type:
            self.showMessage(info_type, info, self.icon)

    class system_message_handler(Handler):
        def __init__(self, tray_icon):
            Handler.__init__(self)
            self.tray_icon = tray_icon
            formatter = Formatter('%(message)s')
            self.setLevel('INFO')
            self.setFormatter(formatter)
            self.pattern = r'(<.+>)(.+)'

        def emit(self, record):
            try:
                msg = self.format(record)
                info_re = re.search(self.pattern, msg)
                if info_re:
                    info_type = info_re.group(1)
                    info = info_re.group(2)
                    self.tray_icon.push_message(info_type, info)
            except Exception as e:
                print(e)
