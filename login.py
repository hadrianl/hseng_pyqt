# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(345, 157)
        self.buttonBox = QtWidgets.QDialogButtonBox(LoginWindow)
        self.buttonBox.setGeometry(QtCore.QRect(230, 30, 81, 91))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayoutWidget = QtWidgets.QWidget(LoginWindow)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 10, 221, 131))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.UserName = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.UserName.setObjectName("UserName")
        self.gridLayout.addWidget(self.UserName, 0, 1, 1, 1)
        self.Password = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.Password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.Password.setObjectName("Password")
        self.gridLayout.addWidget(self.Password, 2, 1, 1, 1)
        self.label_2.setBuddy(self.UserName)
        self.label.setBuddy(self.Password)

        self.retranslateUi(LoginWindow)
        self.buttonBox.rejected.connect(LoginWindow.reject)
        self.buttonBox.accepted.connect(LoginWindow.login_check)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "实盘分析登入"))
        self.label_2.setText(_translate("LoginWindow", "用户名"))
        self.label.setText(_translate("LoginWindow", "密码"))
        self.UserName.setPlaceholderText(_translate("LoginWindow", "kairuitouzi"))

