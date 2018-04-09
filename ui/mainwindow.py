# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1220, 781)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(1200, 30))
        self.widget.setObjectName("widget")
        self.pushButton_console = QtWidgets.QPushButton(self.widget)
        self.pushButton_console.setGeometry(QtCore.QRect(1140, 0, 75, 23))
        self.pushButton_console.setObjectName("pushButton_console")
        self.pushButton_order = QtWidgets.QPushButton(self.widget)
        self.pushButton_order.setGeometry(QtCore.QRect(1060, 0, 75, 23))
        self.pushButton_order.setObjectName("pushButton_order")
        self.verticalLayout.addWidget(self.widget)
        self.QVBoxLayout_ohlc = QtWidgets.QVBoxLayout()
        self.QVBoxLayout_ohlc.setObjectName("QVBoxLayout_ohlc")
        self.QWidget_ohlc = OHlCWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QWidget_ohlc.sizePolicy().hasHeightForWidth())
        self.QWidget_ohlc.setSizePolicy(sizePolicy)
        self.QWidget_ohlc.setMinimumSize(QtCore.QSize(400, 400))
        self.QWidget_ohlc.setObjectName("QWidget_ohlc")
        self.QVBoxLayout_ohlc.addWidget(self.QWidget_ohlc)
        self.verticalLayout.addLayout(self.QVBoxLayout_ohlc)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1220, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_console.setText(_translate("MainWindow", "console"))
        self.pushButton_order.setText(_translate("MainWindow", "order"))

from data_visualize.OHLC_ui import OHlCWidget
