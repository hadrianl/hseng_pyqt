#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:02
# @Author  : Hadrianl 
# @File    : __init__.py.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from PyQt5.Qt import QMainWindow
from ui.mainwindow import Ui_MainWindow
from data_visualize.graph import *
from functools import partial

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

    def init_data_signal(self, extra_data):
        ohlc = self.QWidget_ohlc.data['ohlc']
        for i, n in enumerate(ohlc.extra_data):
            self.comboBox.addQCheckBox(i, n)
            self.comboBox.qCheckBox[i].setChecked(True)
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda n,x: ohlc + extra_data[n] if x else ohlc - extra_data[n], i))
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda name, x: getattr(self, f'checkBox_{name}').setChecked(x),n))
    def init_main_signal(self):
        w_ohlc = self.QWidget_ohlc
        self.pushButton_console.released.connect(w_ohlc.console.show)
        self.checkBox_Trade_Data.toggled.connect(lambda x: (w_ohlc.init_graph(Graph_Trade_Data_Mark(w_ohlc.main_plt)),
                                                           w_ohlc.update_graph('Trade_Data')) if x else w_ohlc.deinit_graph('Trade_Data'))
        self.checkBox_MACD_HL_MARK.toggled.connect(lambda x: (w_ohlc.init_graph(Graph_MACD_HL_MARK(w_ohlc.main_plt)),
                                                             w_ohlc.update_graph('MACD_HL_MARK')) if x else w_ohlc.deinit_graph('MACD_HL_MARK'))
        self.checkBox_MACD.toggled.connect(lambda x: (w_ohlc.init_graph(Graph_MACD(w_ohlc.indicator_plt)),
                                                     w_ohlc.update_graph('MACD')) if x else w_ohlc.deinit_graph('MACD'))
        self.checkBox_STD.toggled.connect(lambda x: (w_ohlc.init_graph(Graph_STD(w_ohlc.indicator2_plt)),
                                                    w_ohlc.update_graph('STD'))if x else w_ohlc.deinit_graph('STD'))
        self.checkBox_MA.toggled.connect(lambda x: (w_ohlc.init_graph(Graph_MA(w_ohlc.main_plt)),
                                                   w_ohlc.update_graph('MA'))if x else w_ohlc.deinit_graph('MA'))