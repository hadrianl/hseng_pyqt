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

    def init_data_signal(self):
        w_ohlc = self.QWidget_ohlc
        ohlc = w_ohlc.data['ohlc']
        extra_data = ohlc.extra_data
        for i, (name, data) in enumerate(extra_data.items()):
            self.comboBox.addQCheckBox(i, name)
            self.comboBox.qCheckBox[i].setChecked(True)
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda data, x: data.activate() if x else data.inactivate(), data))
            self.comboBox.qCheckBox[i].toggled.connect(partial(lambda g_name, x:(w_ohlc.init_graph(g_name), w_ohlc.update_graph(g_name)) if x else w_ohlc.deinit_graph(g_name), name))
