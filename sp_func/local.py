#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 0028 13:39
# @Author  : Hadrianl 
# @File    : local.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from spapi.sub_client import SpFunc
from spapi.spAPI import *
from util import S_logger
import datetime as dt
import sys



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


local_login = False
def addOrder(**kwargs):
    if local_login:
        add_order(**kwargs)
    else:
        print(2, kwargs)

def info_handle(type, info, info_struct=None, handle_type=0):
    if handle_type == 0:
        S_logger.info('*LOCAL*' + type + info)
    elif handle_type == 1:
        S_logger.error('*LOCAL*' + type + info)




def init_spapi():
    info = {'host' : 'demo.spsystem1.info',
            'port':8080,
            'License':'59493B8B4C09F',
            'app_id':'SPDEMO',
            'user_id':'DEMO201706051A',
            'password':'1234'
            }

    # info.update(user_id=user_id, password=password)
    if initialize() == 0:
        info_handle('<API>','初始化成功')
        set_login_info(**info)
        info_handle('<连接>', f"设置登录信息-host:{info['host']} port:{info['port']} license:{info['License']} app_id:{info['app_id']} user_id:{info['user_id']}")
        login()

@on_login_reply  # 登录调用
def reply(user_id, ret_code, ret_msg):
    if ret_code == 0:
        global local_login
        info_handle('<账户>', f'{user_id.decode()}登录成功')
        local_login = True
    else:
        info_handle('<账户>', f'{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')
        local_login = False

@on_account_info_push  # 普通客户登入后返回登入前的户口信息
def account_info_push(acc_info):
    info_handle('<账户>',
                f'{acc_info.ClientId.decode()}信息--NAV:{acc_info.NAV}-BaseCcy:{acc_info.BaseCcy.decode()}-BuyingPower:{acc_info.BuyingPower}-CashBal:{acc_info.CashBal}')

@on_load_trade_ready_push  # 登入后，登入前已存的成交信息推送
def trade_ready_push(rec_no, trade):
    info_handle('<成交>',
                f'历史成交记录--NO:{rec_no}--{trade.OpenClose.decode()}成交@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}')

@on_account_position_push  # 普通客户登入后返回登入前的已存在持仓信息
def account_position_push(pos):
    info_handle('<持仓>',
                f'历史持仓信息--ProdCode:{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-PL:{pos.PL}-Qty:{pos.Qty}-DepQty:{pos.DepQty}',
                pos)

@on_business_date_reply  # 登录成功后会返回一个交易日期
def business_date_reply(business_date):
    info_handle('<日期>', f'当前交易日--{dt.datetime.fromtimestamp(business_date)}')

# ----------------------------------------行情数据主推---------------------------------------------------------------------------------------------------
@on_ticker_update  # ticker数据推送
def ticker_update(ticker):
    ...

@on_api_price_update  # price数据推送
def price_update(price):
    ...
# -------------------------------------------------------------------------------------------------------------------------------------------------------

@on_connecting_reply  # 连接状态改变时调用
def connecting_reply(host_id, con_status):
    info_handle('<连接>', f'{HOST_TYPE[host_id]}状态改变--{HOST_CON_STATUS[con_status]}')

# -----------------------------------------------登入后的新信息回调------------------------------------------------------------------------------
@on_order_request_failed  # 订单请求失败时候调用
def order_request_failed(action, order, err_code, err_msg):
    info_handle('<订单>', f'请求失败--ACTION:{action}-@{order.ProdCode.decode()}-Price:{order.Price}-Qty:{order.Qty}-BuySell:{order.BuySell.decode()}      errcode;{err_code}-errmsg:{err_msg.decode()}', order)

@on_order_before_send_report  # 订单发送前调用
def order_before_snd_report(order):
    info_handle('<订单>', f'即将发送请求--@{order.ProdCode.decode()}-Price:{order.Price}-Qty:{order.Qty}-BuySell:{order.BuySell.decode()}', order)

@on_trade_report  # 成交记录更新后回调出推送新的成交记录
def trade_report(rec_no, trade):
    info_handle('<成交>', f'{rec_no}新成交{trade.OpenClose.decode()}--@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}', trade)

@on_updated_account_position_push  # 新持仓信息
def updated_account_position_push(pos):
    info_handle('<持仓>', f'信息变动--@{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-PL:{pos.PL}-Qty:{pos.Qty}-DepQty:{pos.DepQty}', pos)

@on_updated_account_balance_push  # 户口账户发生变更时的回调，新的账户信息
def updated_account_balance_push(acc_bal):
    info_handle('<结余>', f'信息变动-{acc_bal.Ccy.decode()}-CashBF:{acc_bal.CashBF}-TodayCash:{acc_bal.TodayCash}-NotYetValue:{acc_bal.NotYetValue}-Unpresented:{acc_bal.Unpresented}-TodayOut:{acc_bal.TodayOut}', acc_bal)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------请求回调函数------------------------------------------------------------------------------------
@on_order_report  # 订单报告的回调推送
def order_report(rec_no, order):
    info_handle('<订单>', f'编号:{rec_no}-@{order.ProdCode.decode()}-Status:{ORDER_STATUS[order.Status]}', order)

@on_instrument_list_reply  # 产品系列信息的回调推送，用load_instrument_list()触发
def inst_list_reply(req_id, is_ready, ret_msg):
    if is_ready:
        info_handle('<产品>', f'信息加载成功      req_id:{req_id}-msg:{ret_msg.decode()}')
    else:
        info_handle('<产品>', f'信息正在加载......req_id{req_id}-msg:{ret_msg.decode()}')

@on_product_list_by_code_reply  # 根据产品系列名返回合约信息
def product_list_by_code_reply(req_id, inst_code, is_ready, ret_msg):
    if is_ready:
        if inst_code == '':
            info_handle('<合约>', f'该产品系列没有合约信息      req_id:{req_id}-msg:{ret_msg.decode()}')
        else:
            info_handle('<合约>', f'产品:{inst_code.decode()}合约信息加载成功      req_id:{req_id}-msg:{ret_msg.decode()}')
    else:
        info_handle('<合约>', f'产品:{inst_code.decode()}合约信息正在加载......req_id:{req_id}-msg:{ret_msg.decode()}')

@on_pswchange_reply  # 修改密码调用
def pswchange_reply(ret_code, ret_msg):
    if ret_code == 0:
        info_handle('<密码>', '修改成功')
    else:
        info_handle('<密码>', f'修改失败  errcode:{ret_code}-errmsg:{ret_msg.decode()}')

def deinit_spapi():
    if logout() == 0:
        info_handle('<连接>',f'{c_char_p_user_id.value.decode()}登出请求发送成功')
        if unintialize() == 0:
            info_handle('<API>','释放成功')
            global local_login
            local_login = False

