#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/31 0031 15:12
# @Author  : Hadrianl 
# @File    : Console_ui.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from ui.console import Ui_Console
from PyQt5.Qt import QWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import datetime as dt
from logging import Handler, Formatter


class AnalysisConsole(QWidget, Ui_Console):
    def __init__(self, namespace):
        QWidget.__init__(self)
        Ui_Console.__init__(self)
        help_text = f'''实盘分析Console测试（help_doc()调用帮助文档）'''
        self.setupUi(self)
        self.logging_handler = self.console_logging_handler(self.ConsoleWidget_con)
        self.ConsoleWidget_con.localNamespace = namespace
        self.ConsoleWidget_con.output.setPlainText(f'{help_text}\n')

    def focus(self):
        if self.isHidden():
            self.show()
        else:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.focusWidget()

    def update_daterange(self, start, end):
        self.DateTimeEdit_start.setDateTime(start)
        self.DateTimeEdit_end.setDateTime(end)

    def add_ticker_to_table(self, ticker):
        self.TableWidget_tickers.insertRow(0)
        self.TableWidget_tickers.setItem(0, 0, QTableWidgetItem(dt.datetime.fromtimestamp(ticker.TickerTime).strftime('%H:%M:%S')))
        self.TableWidget_tickers.setItem(0, 1, QTableWidgetItem(str(ticker.Price)))
        qty = QTableWidgetItem(str(ticker.Qty))
        self.TableWidget_tickers.setItem(0, 2, qty)
        if self.TableWidget_tickers.rowCount() > 100:
            self.TableWidget_tickers.removeRow(100)

    def add_price_to_table(self, price):
        max_depth = 5
        for i, bid, bid_qty, ask, ask_qty in zip(range(20), price.Bid, price.BidQty, price.Ask, price.AskQty):
            self.TableWidget_prices.setItem(5+i, 0, QTableWidgetItem(str(bid)))
            self.TableWidget_prices.setItem(5+i, 1, QTableWidgetItem(str(bid_qty)))
            self.TableWidget_prices.setItem(4-i, 0, QTableWidgetItem(str(ask)))
            self.TableWidget_prices.setItem(4-i, 1, QTableWidgetItem(str(ask_qty)))
            if max_depth == i + 1:
                break

    class console_logging_handler(Handler):
        def __init__(self, consolewidget):
            Handler.__init__(self)
            self.consolewidget = consolewidget
            formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.setLevel('INFO')
            self.setFormatter(formatter)

        def emit(self, record):
            msg = self.format(record)
            try:
                self.consolewidget.write(f'{msg}\n')
            except Exception as e:
                print(e)



