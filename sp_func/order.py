#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 0028 13:39
# @Author  : Hadrianl 
# @File    : order.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from spapi.sub_client import SpFunc



# def add_limit_order(prodcode, bs, qty, price, OrderId=''):
#     price = float(price)
#     qty = int(qty)
#     Add_normal_order(prodcode, bs, qty, price, ClOrderId=OrderId)
#
# def add_market_order(prodcode, bs, qty, OrderId=''):
#     qty = int(qty)
#     Add_normal_order(prodcode, bs, qty, ClOrderId=OrderId)
#
# def add_auction_order(prodcode, bs, qty, OrderId=''):
#     qty = int(qty)
#     Add_normal_order(prodcode, bs, qty, AO=True, ClOrderId=OrderId)

def add_order(**kwargs):
    print(kwargs)