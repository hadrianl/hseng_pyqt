#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 0028 13:39
# @Author  : Hadrianl 
# @File    : order.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from spapi.sub_client import Add_normal_order


def add_limit_order(prodcode, bs, qty, price, OrderId=''):
    Add_normal_order(prodcode, bs, qty, price, ClOrderId=OrderId)

def add_market_order(prodcode, bs, qty, OrderId=''):
    Add_normal_order(prodcode, bs, qty, OrderType = 6, ClOrderId=OrderId)

def add_auction_order(prodcode, bs, qty, OrderId=''):
    Add_normal_order(prodcode, bs, qty, OrderType=2, ClOrderId=OrderId)