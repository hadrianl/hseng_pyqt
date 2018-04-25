#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/30 0030 11:40
# @Author  : Hadrianl 
# @File    : local.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from PyQt5.Qt import QDialog
from PyQt5 import QtWidgets, QtCore
import sys
from ui.order_dialog import Ui_Dialog
from ui.acc_info import Ui_Form
import datetime as dt
from sp_func.local import addOrder

class OrderDialog(QDialog, Ui_Dialog):
    def __init__(self):
        QDialog.__init__(self)
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self._price_flag = True
        self.init_state()
        self.init_signal()

    def init_state(self):
        self.dateEdit_ValidTime.setDate(dt.datetime.now().date())
        self.spinBox_market_level.setDisabled(True)
        self.label_ValidTime.setHidden(True)
        self.dateEdit_ValidTime.setHidden(True)
        self.spinBox_Price.setSpecialValueText(' ')
        self.spinBox_StopLevel.setSpecialValueText(' ')
        self.spinBox_StopLevel2.setSpecialValueText(' ')
        self.spinBox_oco_StopLevel.setSpecialValueText(' ')
        # self.spinBox_Price.set


    def init_signal(self):
        self.comboBox_CondType.activated.connect(lambda n: (self.spinBox_Price.setDisabled(n in [1]),
                                                            self.checkBox_Auction.setHidden(n in [1, 2, 3, 4]),
                                                            self.checkBox_Auction.setCheckState(0),
                                                            self.checkBox_Market.setHidden(n in [1, 2, 4]),
                                                            self.checkBox_Market.setCheckState(0),
                                                            self.checkBox_stop_tri.setCheckState(0),
                                                            self.comboBox_ValidType.setCurrentIndex(0),
                                                            self.checkBox_invalid.setEnabled(n in [0, 3]),
                                                            self.checkBox_invalid.setCheckable(n in [0, 3]),
                                                            self.pushButton_buy.setHidden(n in [1, 2]),
                                                            self.pushButton_sell.setHidden(n in [1, 2]),
                                                            self.spinBox_Price.setValue(0) if n in [2] else ...,
                                                            setattr(self, '_price_flag', True)
                                                            ))

        self.comboBox_ValidType.currentIndexChanged.connect(lambda n: (
                                                             self.checkBox_stop_tri.setCheckState(0) if n in [1, 2] else ...,
                                                             self.checkBox_Auction.setEnabled(n in [0]),
                                                             self.checkBox_Market.setEnabled(n in [0]),
                                                             self.checkBox_stop_tri.setEnabled(n in [0, 3, 4]),
                                                             self.dateEdit_ValidTime.setVisible(n in [4]),
                                                             self.dateEdit_ValidTime.setEnabled(n in [4]),
                                                             self.label_ValidTime.setVisible(n in [4]),
                                                             ))
        self.checkBox_stop_tri.toggled.connect(lambda x: (self.comboBox_StopType.setCurrentIndex(0) if not x else ...,
                                                          self.spinBox_StopLevel.setValue(0) if not x else ...))

        self.checkBox_Market.toggled.connect(lambda x: (self.spinBox_Price.setValue(0) if x else ...,
                                                        ))
        self.checkBox_Auction.toggled.connect(lambda x: (self.spinBox_Price.setValue(0x7fffffff) if x else self.spinBox_Price.setValue(0),
                                                         ))

        self.comboBox_StopType.activated.connect(lambda n: self.checkBox_Market.setChecked(n in [3]))

        self.spinBox_StopLevel2.valueChanged.connect(lambda x: self.spinBox_Price.setValue(x + self.spinBox_toler.value()if self.radioButton_buy1.isChecked() else x - self.spinBox_toler.value())if not self.checkBox_Market.checkState() else 0)
        self.spinBox_toler.valueChanged.connect(lambda x: self.spinBox_Price.setValue((x + self.spinBox_StopLevel2.value() if self.radioButton_buy1.isChecked() else self.spinBox_StopLevel2.value() - x) if not self.checkBox_Market.checkState() else 0))
        self.radioButton_buy1.toggled.connect(lambda x: self.spinBox_Price.setValue(self.spinBox_StopLevel2.value() + self.spinBox_toler.value()))
        self.radioButton_sell1.toggled.connect(lambda x: self.spinBox_Price.setValue(self.spinBox_StopLevel2.value() - self.spinBox_toler.value()))

        self.spinBox_oco_StopLevel.valueChanged.connect(lambda x: self.label_oco_pirce.setText(f'{x + self.spinBox_oco_toler.value() if self.radioButton_buy2.isChecked() else x - self.spinBox_oco_toler.value()}'))
        self.spinBox_oco_toler.valueChanged.connect(lambda x: self.label_oco_pirce.setText(f'{x + self.spinBox_oco_StopLevel.value() if self.radioButton_buy2.isChecked() else self.spinBox_oco_StopLevel.value() - x}'))
        self.radioButton_buy2.toggled.connect(lambda x: self.label_oco_pirce.setText(f'{self.spinBox_oco_StopLevel.value() + self.spinBox_oco_toler.value()}'))
        self.radioButton_sell1.toggled.connect(lambda x: self.label_oco_pirce.setText(f'{self.spinBox_oco_StopLevel.value() - self.spinBox_oco_toler.value()}'))

        self.spinBox_Price.valueChanged.connect(lambda x: (self.spinBox_Price.setValue(30000), setattr(self, '_price_flag', False)) if self._price_flag else ...)
        self.spinBox_StopLevel.valueChanged.connect(lambda x: (self.spinBox_StopLevel.setValue(30000), setattr(self, '_price_flag', False)) if self._price_flag else ...)
        self.spinBox_StopLevel2.valueChanged.connect(lambda x: (self.spinBox_StopLevel2.setValue(30000), setattr(self, '_price_flag', False)) if self._price_flag else ...)
        self.spinBox_oco_StopLevel.valueChanged.connect(lambda x: (self.spinBox_oco_StopLevel.setValue(30000), setattr(self, '_price_flag', False)) if self._price_flag == 1 else ...)
        self.pushButton_buy.released.connect(lambda :self.order('B'))
        self.pushButton_sell.released.connect(lambda :self.order('S'))


    def order(self, BuySell):
        try:
            order_kwargs = {}
            order_kwargs['BuySell'] = BuySell
            order_kwargs['ProdCode'] = self.lineEdit_ProdCode.text()
            order_kwargs['Qty'] = self.spinBox_Qty.value()
            order_kwargs['Ref'] = self.lineEdit_Ref.text()
            order_kwargs['OrderOption'] = self.checkBox_OrderOptions.checkState()
            _condtype_index = self.comboBox_CondType.currentIndex()
            order_kwargs['CondType'] = {0: 0, 1: 1, 2: 4,3: 0, 4: 3}[_condtype_index]

            if _condtype_index == 0:
                _order_type = (self.checkBox_Auction.checkState() << 1) + self.checkBox_Market.checkState()
                order_kwargs['OrderType'] = {0: 0, 2: 6, 4: 2}[_order_type]
                order_kwargs['Price'] = {0: self.spinBox_Price.value(), 2: 0, 4: 0x7fffffff}[_order_type]
                order_kwargs['ValidType'] = self.comboBox_ValidType.currentIndex()
                if order_kwargs['ValidType'] == 4:
                    order_kwargs['ValidTime'] = int(dt.datetime.strptime(self.dateEdit_ValidTime.date().toPyDate().strftime('%Y/%m/%d'),
                                                         '%Y/%m/%d').timestamp())
                if self.checkBox_stop_tri.isChecked():
                    order_kwargs['StopType'] = {0: 'L', 1: 'U', 2: 'D', 3: 'L'}[self.comboBox_StopType.currentIndex()]
                    order_kwargs['StopLevel'] = self.spinBox_StopLevel.value()
                    order_kwargs['CondType'] = 1
                else:
                    order_kwargs['StopLevel'] = 0
            elif _condtype_index == 1:
                order_kwargs['StopType'] = 'L'
                order_kwargs['Price'] = self.spinBox_StopLevel2.value() + self.spinBox_toler.value() if BuySell == 'B' \
                    else self.spinBox_StopLevel2.value() - self.spinBox_toler.value()
                order_kwargs['StopLevel'] = self.spinBox_StopLevel2.value()
                if self.checkBox_Trailing_Stop.isChecked():
                    order_kwargs['CondType'] = 6
                    order_kwargs['ValidType'] = 0
                    if BuySell == 'B':
                        order_kwargs['DownLevel'] = self.spinBox_trailing_stop_step.value()
                    else:
                        order_kwargs['UpLevel'] = self.spinBox_trailing_stop_step.value()
            elif _condtype_index == 2:
                order_kwargs['ValidType'] = 0
                order_kwargs['Price'] = self.spinBox_Price.value()
                if BuySell == 'B':
                    order_kwargs['UpLevel'] = self.spinBox_oco_StopLevel.value()
                    order_kwargs['UpPrice'] = self.spinBox_oco_StopLevel.value() + self.spinBox_oco_toler.value()
                else:
                    order_kwargs['DownLevel'] = self.spinBox_oco_StopLevel.value()
                    order_kwargs['DownPrice'] = self.spinBox_oco_StopLevel.value() - self.spinBox_oco_toler.value()
                ...
            elif _condtype_index == 3:
                order_kwargs['ValidType'] = 0
                _profit = self.spinBox_bullbear_profit.value()
                _loss = self.spinBox_bullbear_loss.value()
                _loss_toler = self.spinBox_bullbear_loss_toler.value()
                order_kwargs['Price'] = Price = self.spinBox_Price.value()
                if BuySell == 'B':
                    order_kwargs['UpLevel'] = Price + _profit
                    order_kwargs['UpPrice'] = Price + _profit
                    order_kwargs['DownLevel'] = Price - _loss
                    order_kwargs['DownPrice'] = Price - _loss - _loss_toler
                else:
                    order_kwargs['DownLevel'] = Price - _profit
                    order_kwargs['DownPrice'] = Price - _profit
                    order_kwargs['UpLevel'] = Price + _loss
                    order_kwargs['UpPrice'] = Price + _loss + _loss_toler
                ...
            elif _condtype_index == 4:
                order_kwargs['ValidType'] = 0
                order_kwargs['Price'] = self.spinBox_Price.value()
                order_kwargs['SchedTime'] = int(self.dateTimeEdit_sched_time.dateTime().toPyDateTime().timestamp())
        except Exception as e:
            raise e
        addOrder(**order_kwargs)


class AccInfoWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        Ui_Form.__init__(self)
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    od = OrderDialog()
    od.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec())