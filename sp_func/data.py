#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/30 0030 14:14
# @Author  : Hadrianl 
# @File    : data.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from spapi.sub_client import SpFunc
from util import F_logger

# def get_order
def init_data_sub(symbol_list):
    spfunc = SpFunc()
    try:
        for s in symbol_list:
            if s not in spfunc.sub_ticker_list():
                spfunc.sub_ticker(s)

            if s not in spfunc.sub_price_list():
                spfunc.sub_price(s)
            F_logger.info(f'初始化数据{s}订阅成功')
    except Exception as e:
        F_logger.error(f'初始化数据订阅错误--{e}')
    else:
        F_logger.info(f'初始化数据订阅完成')

def load_product_info(symbol_list):
    spfunc = SpFunc()
    try:
        server_product_info = spfunc._s('get_product_by_array')
        print(server_product_info)
        server_product_code = {p.ProdCode.decode() for p in server_product_info}
        inst_code_list = {s[0:3] for s in symbol_list if s not in server_product_code}
        for i in inst_code_list:
            spfunc._s('load_productinfolist_by_code', i)
            F_logger.info(f'请求服务器加载产品{i}成功')
    except Exception as e:
        F_logger.error(f'请求服务器加载产品失败--{e}')
    else:
        F_logger.info(f'请求服务器加载产品信息列表完成')


def get_product_info(symbol_list):
    spfunc = SpFunc()
    product_info = {}

    try:
        for s in symbol_list:
            product_info[s] = spfunc._s('get_product_by_code', s)
            F_logger.info(f'加载产品{s}成功')
    except Exception as e:
        F_logger.error(f'加载产品{s}错误--{e}')
    else:
        F_logger.info(f'加载产品信息列表完成')

    return product_info
