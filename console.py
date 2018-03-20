# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'console.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Console(object):
    def setupUi(self, Console):
        Console.setObjectName("Console")
        Console.resize(1050, 741)
        self.consolewidget = ConsoleWidget(Console)
        self.consolewidget.setGeometry(QtCore.QRect(10, 70, 731, 661))
        self.consolewidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.consolewidget.setObjectName("consolewidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(Console)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 271, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.resample_Layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.resample_Layout.setContentsMargins(0, 0, 0, 0)
        self.resample_Layout.setObjectName("resample_Layout")
        self.min_1 = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.min_1.setChecked(True)
        self.min_1.setObjectName("min_1")
        self.resample_Layout.addWidget(self.min_1)
        self.min_5 = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.min_5.setObjectName("min_5")
        self.resample_Layout.addWidget(self.min_5)
        self.min_10 = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.min_10.setObjectName("min_10")
        self.resample_Layout.addWidget(self.min_10)
        self.min_30 = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.min_30.setObjectName("min_30")
        self.resample_Layout.addWidget(self.min_30)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(Console)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(300, 10, 439, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dateTime_start = QtWidgets.QDateTimeEdit(self.horizontalLayoutWidget_2)
        self.dateTime_start.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.dateTime_start.setDateTime(QtCore.QDateTime(QtCore.QDate(2018, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateTime_start.setCurrentSection(QtWidgets.QDateTimeEdit.HourSection)
        self.dateTime_start.setCalendarPopup(True)
        self.dateTime_start.setObjectName("dateTime_start")
        self.horizontalLayout.addWidget(self.dateTime_start)
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.dateTime_end = QtWidgets.QDateTimeEdit(self.horizontalLayoutWidget_2)
        self.dateTime_end.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.dateTime_end.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.dateTime_end.setDateTime(QtCore.QDateTime(QtCore.QDate(2018, 3, 20), QtCore.QTime(0, 0, 0)))
        self.dateTime_end.setCurrentSection(QtWidgets.QDateTimeEdit.HourSection)
        self.dateTime_end.setCalendarPopup(True)
        self.dateTime_end.setObjectName("dateTime_end")
        self.horizontalLayout.addWidget(self.dateTime_end)
        self.Button_daterange = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.Button_daterange.setObjectName("Button_daterange")
        self.horizontalLayout.addWidget(self.Button_daterange)

        self.retranslateUi(Console)
        QtCore.QMetaObject.connectSlotsByName(Console)

    def retranslateUi(self, Console):
        _translate = QtCore.QCoreApplication.translate
        Console.setWindowTitle(_translate("Console", "Form"))
        self.min_1.setText(_translate("Console", "1min"))
        self.min_5.setText(_translate("Console", "5min"))
        self.min_10.setText(_translate("Console", "10min"))
        self.min_30.setText(_translate("Console", "30min"))
        self.dateTime_start.setDisplayFormat(_translate("Console", "M/d dddd H:mm"))
        self.label.setText(_translate("Console", "->"))
        self.dateTime_end.setDisplayFormat(_translate("Console", "M/d dddd H:mm"))
        self.Button_daterange.setText(_translate("Console", "跳转"))

from pyqtgraph.console import ConsoleWidget
