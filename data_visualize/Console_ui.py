#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/31 0031 15:12
# @Author  : Hadrianl 
# @File    : Console_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


import pyqtgraph.console
from util import V_logger
from console import *
from PyQt5.Qt import QWidget, QTableWidgetItem, QColor
from PyQt5.QtCore import Qt
import datetime as dt


class AnalysisConsole(QWidget, Ui_Console):
    def __init__(self, namespace):
        QWidget.__init__(self)
        Ui_Console.__init__(self)
        help_text = f'''实盘分析Console测试（help_doc()调用帮助文档）'''
        self.setupUi(self)
        self.consolewidget.localNamespace = namespace
        self.consolewidget.output.setPlainText(help_text)

    def focus(self):
        if self.isHidden():
            self.show()
        else:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.focusWidget()

    def update_daterange(self, start, end):
        self.dateTime_start.setDateTime(start)
        self.dateTime_end.setDateTime(end)

    def add_ticker_to_table(self, ticker):
        self.tickers_tableWidget.insertRow(0)
        self.tickers_tableWidget.setItem(0, 0, QTableWidgetItem(dt.datetime.fromtimestamp(ticker.TickerTime).strftime('%H:%M:%S')))
        self.tickers_tableWidget.setItem(0, 1, QTableWidgetItem(str(ticker.Price)))
        qty = QTableWidgetItem(str(ticker.Qty))
        qty.setBackground(QColor('r')) if ticker.Qty >= 10 else ...
        self.tickers_tableWidget.setItem(0, 2, qty)
        if self.tickers_tableWidget.rowCount() > 100:
            self.tickers_tableWidget.removeRow(100)
