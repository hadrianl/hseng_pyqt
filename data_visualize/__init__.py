#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/18 0018 14:02
# @Author  : Hadrianl 
# @File    : __init__.py.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from PyQt5.Qt import QMainWindow
from mainwindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)