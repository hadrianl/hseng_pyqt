#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 16:54
# @Author  : Hadrianl 
# @File    : baseitems.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.Qt import QFont
import time
from abc import ABC, abstractmethod
from util import V_logger
import datetime as dt

class CandlestickItem(pg.GraphicsObject):
    """
    蜡烛图的图形件
    """

    def __init__(self):
        pg.GraphicsObject.__init__(self)
        self.flagHasData = False
        self.picture = QtGui.QPicture()
        self.PenWidth = 0.4
        self.WLinePen = pg.mkPen('w', width=self.PenWidth)
        self.GLinePen = pg.mkPen('g', width=self.PenWidth)
        self.RLinePen = pg.mkPen('r', width=self.PenWidth)
        self.GreenBrush = pg.mkBrush('g')
        self.RedBrush = pg.mkBrush('r')
        self.is_current_bar = False
        self.hline = pg.InfiniteLine(angle=0, movable=False, pen=self.WLinePen)

    def mark_line(self):
        self.is_current_bar = True
        self.htext = pg.InfLineLabel(self.hline)

    def setHisData(self, ohlc):
        length = len(ohlc.data)
        self.ohlc_x = ohlc.x.iloc[0: (length-1)]
        self.ohlc_data = ohlc.data.iloc[0: (length-1)]
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def setCurData(self, ohlc):
        length = len(ohlc.data)
        self.ohlc_x = ohlc.x.iloc[-1: length]
        self.ohlc_data = ohlc.data.iloc[-1: length]
        self.flagHasData = True
        self.generatePicture()
        self.informViewBoundsChanged()

    def generatePicture(self):
        # pre-computing a QPicture object allows paint() to run much more quickly,
        # rather than re-drawing the shapes every time.
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(self.WLinePen)
        w = self.PenWidth
        for (i, (t, open, high, low, close)) in zip(self.ohlc_x, self.ohlc_data.itertuples()):
            p.drawLine(QtCore.QPointF(i, low), QtCore.QPointF(i, high))
            if self.is_current_bar:
                self.hline.setPos(close)
                self.htext.setText(f'{close}', color='w')
            if open > close:
                p.setBrush(self.GreenBrush)
                self.hline.setPen(self.GLinePen)
            else:
                p.setBrush(self.RedBrush)
                self.hline.setPen(self.RLinePen)
            p.drawRect(QtCore.QRectF(i-w, open, w*2, close-open))
        p.end()

    def paint(self, p, *args):
        if self.flagHasData:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        # boundingRect _must_ indicate the entire area that will be drawn on
        # or else we will get artifacts and possibly crashing.
        # (in this case, QPicture does all the work of computing the bouning rect for us)
        return QtCore.QRectF(self.picture.boundingRect())


class DateAxis(pg.AxisItem):
    """
    时间轴标签件，timestamp转换为string
    """
    def __init__(self, timestamp_mapping, orientation='bottom', *args):
        super(DateAxis, self).__init__(orientation, *args)
        self._timestamp_mapping = timestamp_mapping

    def update_tickval(self, timestamp_mapping):
        self._timestamp_mapping = timestamp_mapping

    def tickStrings(self, values, scale, spacing):
        strns = []
        try:
            timestamp = self._timestamp_mapping.iloc[values]
            rng = max(timestamp)-min(timestamp)

        except Exception as e:
            timestamp = []
            rng =0
        # if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b-%d %H->'
            label2 = ' %b-%d %H, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%dD '
            label1 = '%b,%d ->'
            label2 = ' %b,%d ,%Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y ->'
            label2 = ' %Y'
        elif rng >= 3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        else:
            string = ''
            label1 = ''
            label2 = ''
        for x in timestamp:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except Exception as e:
                # print(e) ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(timestamp)))+time.strftime(label2, time.localtime(max(timestamp)))
        except Exception as e:
            label = ''
        self.setLabel(text=label)
        return strns


class TradeDataScatter(pg.ScatterPlotItem):
    def __init__(self):
        self.PenWidth = 0.4
        super(TradeDataScatter, self).__init__(pen=pg.mkPen('w', width=self.PenWidth))


class TradeDataLinkLine(pg.LineSegmentROI):
    def __init__(self, pen):
        super(TradeDataLinkLine, self).__init__(positions=[[0, 0], [0, 0]], pen=pen, movable=False)
        self.setPen(pen)

    def setData(self, positions, pen=None):
        if pen:
            self.setPen(pen)
        handles = (None, None)
        for i in range(len(self.getHandles())):
            self.removeHandle(0)
        for i, p in enumerate(positions):
            self.addFreeHandle(p, item=handles[i])

    def offset(self,i=1):
        self.setData([[self.handles[0]['item'].pos().x() - i,  self.handles[0]['item'].pos().y()],
                      [self.handles[1]['item'].pos().x() - i,  self.handles[1]['item'].pos().y()]],
                     self.pen)

class graph_base(ABC):
    '''
    图表的基础抽象类，需要实现init，update和deinit方法
    '''
    def __init__(self, plts, name, **kwargs):
        self.plts = {p.vb.name: p for p in plts}
        self.name = name
        self._active = False
        self._crosshair_text = True
        for i in kwargs:
            setattr(self, i, kwargs[i])

    @abstractmethod
    def _init(self, ohlc): ...

    @abstractmethod
    def _deinit(self): ...

    @abstractmethod
    def _update(self, ohlc): ...

    def init(self, ohlc):
        if not self._active:
            data = getattr(ohlc, self.name, None)
            self.text_pos = {}
            self.plt_texts = {}
            self.plt_items = {p_name: {} for p_name in self.plts}
            if data:
                for p in self.plts:
                    self._init(p, ohlc, data)
                    V_logger.info(f'G+初始化{self.name}图表至{p}')
            else:
                for p in self.plts:
                    self._init(p, ohlc)
                    V_logger.info(f'G+初始化{self.name}图表至{p}')
            self._active = True

    def update(self, ohlc):
        if self._active:
            data = getattr(ohlc, self.name, None)
            if data:
                for p in self.plts:
                    self._update(p, ohlc, data)
                    V_logger.info(f'G↑更新{self.name}图表至{p}')
            else:
                for p in self.plts:
                    self._update(p, ohlc)
                    V_logger.info(f'G↑更新{self.name}图表至{p}')

    def deinit(self):
        if self._active:
            for p in self.plts:
                self._deinit(p)
            V_logger.info(f'G-反初始化{self.name}图表')
            self._active = False

    def info_text(self, p, *args, **kwargs):...

    def add_info_text(self, p, anchor=(0, 0), pos=(0,0,1,1), active=True):
        self.text_pos[p] = pos
        self.plt_texts[p] = pg.TextItem(anchor=anchor)
        self.plts[p].addItem(self.plt_texts[p])

    def set_info_text(self, p, *args, **kwargs):
        try:
            if p in self.plt_texts:
                plt = self.plts[p]
                textitem = self.plt_texts[p]
                vbr = plt.vb.viewRange()
                info_text = self.info_text(p, *args, **kwargs)
                textitem.setHtml(info_text)
                p = self.text_pos[p]
                Pos = (vbr[p[0]][p[1]], vbr[p[2]][p[3]])
                textitem.setPos(*Pos)
        except Exception as e:
            V_logger.debug(f'set_info_text设置信息错误->{p}')


    def del_info_text(self, p):
        self.plts[p].removeItem(self.plt_texts.pop(p))

from PyQt5.QtWidgets import QComboBox, QLineEdit, QListWidget, QCheckBox, QListWidgetItem


class ComboCheckBox(QComboBox):
    def __init__(self, parent=None, items = None):  # items==[str,str...]
        super(ComboCheckBox, self).__init__(parent)
        self.items = items if items else []
        self.qCheckBox = []
        self.qLineEdit = QLineEdit()
        self.qLineEdit.setReadOnly(True)
        self.qListWidget = QListWidget()

        self.row_num = len(self.items)
        for i in range(self.row_num):
            self.addQCheckBox(i)
            self.qCheckBox[i].stateChanged.connect(self.show)

        self.setLineEdit(self.qLineEdit)
        self.setModel(self.qListWidget.model())
        self.setView(self.qListWidget)

    def addQCheckBox(self, i, text):
        self.items.insert(i, text)
        self.qCheckBox.append(QCheckBox())
        qItem = QListWidgetItem(self.qListWidget)
        self.qCheckBox[i].setText(self.items[i])
        self.qListWidget.setItemWidget(qItem, self.qCheckBox[i])
        self.qCheckBox[i].stateChanged.connect(self.show)

    def Selectlist(self):
        Outputlist = []
        for i in range(self.row_num):
            if self.qCheckBox[i].isChecked() == True:
                Outputlist.append(self.qCheckBox[i].text())
        return Outputlist

    def show(self):
        show = ''
        self.qLineEdit.setReadOnly(False)
        self.qLineEdit.clear()
        for i in self.Selectlist():
            show += i + ';'
        self.qLineEdit.setText(show)
        self.qLineEdit.setReadOnly(True)

class plt_base(pg.PlotItem):
    def __init__(self, name, date_xaxis):
        super(plt_base, self).__init__(viewBox=pg.ViewBox(), name=name, axisItems={'bottom': date_xaxis})
        # vb = CustomViewBox()
        self.setMenuEnabled(False)
        # self.setClipToView(True)
        self.hideAxis('left')
        self.showAxis('right')
        self.setDownsampling(mode='peak')
        # # self.setRange(xRange=(0, 1), yRange=(0, 1))
        self.getAxis('right').setWidth(30)
        self.getAxis('right').setStyle(tickFont=QFont("Roman times", 6, QFont.Bold))
        self.getAxis('right').setPen(color=(255, 255, 255, 255), width=0.8)
        self.showGrid(True, True)
        self.hideButtons()
        V_logger.info(f'初始化{name}画布')

    def bind(self, layout, row=None, col=None):
        self.layout = layout
        self.layout.addItem(self, row, col)

    def unbind(self):
        self.layout.removeItem(self)