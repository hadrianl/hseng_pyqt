#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 16:54
# @Author  : Hadrianl 
# @File    : baseitems.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import time


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
            label1 = '%b %d-'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d D'
            label1 = '%b - '
            label2 = '%b , %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
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
            # print(e)
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

class graph_base:
    def __init__(self, plt, name):
        self.plt = plt
        self.name = name

    def init(self):
        ...

    def deinit(self):
        ...

    def update(self):
        ...