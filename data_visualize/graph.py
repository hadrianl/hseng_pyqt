#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/10 0010 15:55
# @Author  : Hadrianl 
# @File    : graph.py
# @License : (C) Copyright 2013-2017, 凯瑞投资
from util import V_logger, MA_COLORS
import pandas as pd
import numpy as np
from PyQt5.Qt import  QBrush, QColor
from data_visualize.baseitems import graph_base, TradeDataScatter, TradeDataLinkLine, CandlestickItem
import pyqtgraph as pg


class Graph_OHLC(graph_base):
    def __init__(self, plt):
        super(Graph_OHLC, self).__init__(plt, 'OHLC')

    def _init(self, ohlc):
        self.ohlc = ohlc
        self.items_dict['ohlc'] = CandlestickItem()
        self.items_dict['tick'] = CandlestickItem()
        self.items_dict['hline'] = self.items_dict['tick'].hline
        self.items_dict['tick'].mark_line()
        self.plt.addItem(self.items_dict['ohlc'])
        self.plt.addItem(self.items_dict['tick'])
        self.plt.addItem(self.items_dict['hline'])
        self.add_info_text()

    def _update(self, ohlc):
        self.ohlc = ohlc
        self.items_dict['ohlc'].setHisData(ohlc)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)

    def init(self, ohlc):
        if not self._active:
            self.items_dict = {}
            self._init(ohlc)
            V_logger.info(f'G+初始化{self.name}图表')
            self._active = True
        else:
            V_logger.error(f'G+{self.name}图表已存在')

    def update(self, ohlc):
        if self._active:
            self._update(ohlc)
            V_logger.info(f'G↑更新{self.name}图表')
        else:
            V_logger.info(f'G↑{self.name}图表未初始化')

    def add_info_text(self):
        self.text_item = pg.TextItem(anchor=(0, 0))
        self.plt.addItem(self.text_item)

    def set_info_text(self, x_index):
        try:
            text_df = self.ohlc.data.iloc[x_index]
            vb = self.plt.getViewBox().viewRange()
            html = f"""
                           <span style="color:white;font-size:12px"><span/><span style="color:blue">{str(text_df.name)[8:16].replace(" ", "日")}<span/><br/>
                           <span style="color:white;font-size:12px">开:<span/><span style="color:red">{text_df.open}<span/><br/>
                           <span style="color:white;font-size:12px">高:<span/><span style="color:red">{text_df.high}<span/><br/>
                           <span style="color:white;font-size:12px">低:<span/><span style="color:red">{text_df.low}<span/><br/>
                           <span style="color:white;font-size:12px">收:<span/><span style="color:red">{text_df.close}<span/>
                           """
            self.text_item.setPos(vb[0][0], vb[1][1])
            self.text_item.setHtml(html)
        except IndexError:
            pass





class Graph_MA(graph_base):
    def __init__(self, plt, colors=None):
        super(Graph_MA, self).__init__(plt, 'MA')
        self.colors = colors if colors else MA_COLORS

    def _init(self, ohlc, i_ma):
        for w in i_ma._windows:
            self.items_dict[w] = pg.PlotDataItem(pen=pg.mkPen(color=self.colors.get(w, 'w'), width=1))
            self.plt.addItem(self.items_dict[w])
        self.add_info_text()

    def _update(self, ohlc, i_ma):
        x = ohlc.x
        for w in self.items_dict:
            self.items_dict[w].setData(x, getattr(i_ma, w).values)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)

    def add_info_text(self):
        self.text_item = pg.TextItem(anchor=(1, 0))
        self.plt.addItem(self.text_item)

    def set_info_text(self, x_index):
        try:
            TextItem = self.text_item
            vb = self.plt.vb.viewRange()
            ma_text = [
                f'<span style="color:rgb{MA_COLORS[k]};font-size:12px">MA{k[-2:]}:{round(v.yData[x_index],2)}<span/>'
                for k, v in self.items_dict.items() if k != 'Text']
            TextItem.setHtml('  '.join(ma_text))
            TextItem.setPos(vb[0][1], vb[1][1])
        except Exception:
            pass

class Graph_MACD(graph_base):
    def __init__(self, plt, macd_colors=('g', 'y', 'b', 'r'), diff_colors='y', dea_colors='w'):
        super(Graph_MACD, self).__init__(plt, 'MACD')
        self.macd_colors_map = {i:v for i,v in enumerate(macd_colors)}
        self.diff_colors = diff_colors
        self.dea_colors = dea_colors

    def _init(self, ohlc, i_macd):
        macd_pens = pd.concat([ohlc.close > ohlc.open, i_macd.macd > 0], 1).apply(
            lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map(self.macd_colors_map)
        macd_brushs = [None if (i_macd.macd > i_macd.macd.shift(1))[i]
                       else v for i, v in macd_pens.iteritems()]
        self.items_dict['MACD'] = pg.BarGraphItem(x=ohlc.x, height=i_macd.macd,
                                                       width=0.5, pens=macd_pens, brushes=macd_brushs)
        self.items_dict['diff'] = pg.PlotDataItem(pen=self.diff_colors)
        self.items_dict['dea'] = pg.PlotDataItem(pen=self.dea_colors)
        self.plt.addItem(self.items_dict['MACD'])
        self.plt.addItem(self.items_dict['diff'])
        self.plt.addItem(self.items_dict['dea'])
        self.add_info_text()

    def _update(self, ohlc, i_macd):
        x = i_macd.x
        diff = i_macd.diff
        dea = i_macd.dea
        macd = i_macd.macd
        self.items_dict['diff'].setData(x, diff.values)
        self.items_dict['dea'].setData(x, dea.values)
        macd_pens = pd.concat(
            [ohlc.close > ohlc.open, macd > 0], 1).apply(
            lambda x: (x.iloc[0] << 1) + x.iloc[1], 1).map(self.macd_colors_map)
        macd_brushes = [None if (macd > macd.shift(1))[i]
                        else v for i, v in macd_pens.iteritems()]
        self.items_dict['MACD'].setOpts(x=x, height=macd, pens=macd_pens, brushes=macd_brushes)

    def _deinit(self):
            for k, v in self.items_dict.items():
                self.plt.removeItem(v)

    def add_info_text(self):
        self.text_item = pg.TextItem(anchor=(0, 0))
        self.plt.addItem(self.text_item)

    def set_info_text(self, x_index):
        try:
            macd_text = f'<span style="color:red">MACD:{round(self.items_dict["MACD"].opts["height"][x_index], 2)}<span/>  ' \
                        f'<span style="color:yellow">DIFF:{round(self.items_dict["diff"].yData[x_index], 2)}<span/>  ' \
                        f'<span style="color:white">DEA:{round(self.items_dict["dea"].yData[x_index], 2)}<span/>  '
            self.text_item.setHtml(macd_text)
            self.text_item.setPos(self.plt.vb.viewRange()[0][0], self.plt.vb.viewRange()[1][1])
        except Exception:
            pass

class Graph_MACD_HL_MARK(graph_base):
    def __init__(self, plt, high_color='#FF0000', low_color='#7CFC00'):
        super(Graph_MACD_HL_MARK, self).__init__(plt, 'MACD_HL_MARK')
        self.high_color = high_color
        self.low_color = low_color

    def _init(self, ohlc, h_macd_hl_mark):
        self.items_dict = {}
        self.items_dict['high_pos'] = []
        self.items_dict['low_pos'] = []

    def _update(self,ohlc, h_macd_hl_mark):
        x = ohlc.x
        for i in self.items_dict['high_pos']:
            self.plt.removeItem(i)
        for i in self.items_dict['low_pos']:
            self.plt.removeItem(i)
        self.items_dict['high_pos'].clear()
        self.items_dict['low_pos'].clear()
        for k, v in h_macd_hl_mark.high_pos.iteritems():
            textitem = pg.TextItem(html=f'<span style="color:{self.high_color};font-size:11px">{v}<span/>',
                                   border=pg.mkPen({'color': self.high_color, 'width': 1}),
                                   angle=15, anchor=(0, 1))
            textitem.setPos(x[k], v)
            self.plt.addItem(textitem)
            self.items_dict['high_pos'].append(textitem)

        for k, v in h_macd_hl_mark.low_pos.iteritems():
            textitem = pg.TextItem(html=f'<span style="color:{self.low_color};font-size:11px">{v}<span/>',
                                   border=pg.mkPen({'color': self.low_color, 'width': 1}),
                                   angle=-15, anchor=(0, 0))
            textitem.setPos(x[k], v)
            self.plt.addItem(textitem)
            self.items_dict['low_pos'].append(textitem)

    def _deinit(self):
            for k, v in self.items_dict.items():
                for i in v:
                    self.plt.removeItem(i)

class Graph_STD(graph_base):
    def __init__(self, plt, inc_colors=('g', 'y', 'l', 'b', 'r'), pos_std_color='r', neg_std_color='g'):
        super(Graph_STD, self).__init__(plt, 'STD')
        self.inc_colors = inc_colors
        self.pos_std_color = pos_std_color
        self.neg_std_color = neg_std_color

    def _init(self, ohlc, i_std):
        self.plt.setMaximumHeight(150)
        std_inc_pens = pd.cut((i_std.inc / i_std.std).fillna(0), [-np.inf, -2, -1, 1, 2, np.inf],  # 设置画笔颜色
                              labels=self.inc_colors)
        inc_gt_std = (i_std.inc.abs() / i_std.std) > 1
        std_inc_brushes = np.where(inc_gt_std, std_inc_pens, None)  # 设置画刷颜色
        self.items_dict['inc'] = pg.BarGraphItem(x=i_std.x, height=i_std.inc,
                                                 width=0.5, pens=std_inc_pens, brushes=std_inc_brushes)
        self.items_dict['pos_std'] = pg.PlotDataItem(pen=self.pos_std_color)
        self.items_dict['neg_std'] = pg.PlotDataItem(pen=self.neg_std_color)
        self.items_dict['ratio'] = pg.PlotDataItem()
        self.plt.addItem(self.items_dict['inc'])
        self.plt.addItem(self.items_dict['pos_std'])
        self.plt.addItem(self.items_dict['neg_std'])
        self.add_info_text()

    def _update(self, ohlc, i_std):
        x = ohlc.x
        inc = i_std.inc
        std = i_std.std
        pos_std = i_std.pos_std
        neg_std = i_std.neg_std
        ratio = i_std.ratio
        std_inc_pens = pd.cut((inc / std).fillna(0), [-np.inf, -2, -1, 1, 2, np.inf],
                              labels=self.inc_colors)
        inc_gt_std = (inc.abs() / std) > 1
        std_inc_brushes = np.where(inc_gt_std, std_inc_pens, None)
        self.items_dict['pos_std'].setData(x, pos_std)
        self.items_dict['neg_std'].setData(x, neg_std)
        self.items_dict['ratio'].setData(x, ratio)
        self.items_dict['inc'].setOpts(x=x, height=inc, pens=std_inc_pens, brushes=std_inc_brushes)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)

    def add_info_text(self):
        self.text_item = pg.TextItem(anchor=(0, 0))
        self.plt.addItem(self.text_item)

    def set_info_text(self, x_index):
        try:
            std_text = f'<span style="color:yellow">INC:{round(self.items_dict["inc"].opts["height"][x_index], 2)}<span/> ' \
                       f'<span style="color:red">POS_STD:{round(self.items_dict["pos_std"].yData[x_index], 2)}<span/> ' \
                       f'<span style="color:green">NEG_STD:{round(self.items_dict["neg_std"].yData[x_index], 2)}<span/> ' \
                       f'<span style="color:white">RATIO:{round(self.items_dict["ratio"].yData[x_index], 2)}<span/> '
            self.text_item.setHtml(std_text)
            self.text_item.setPos(self.plt.vb.viewRange()[0][0], self.plt.vb.viewRange()[1][1])
        except Exception:
            pass

class Graph_Trade_Data_Mark(graph_base):
    def __init__(self, plt, long_symbol='t1', short_symbol='t'):
        super(Graph_Trade_Data_Mark, self).__init__(plt, 'Trade_Data')
        self.long_symbol = long_symbol
        self.short_symbol = short_symbol

    def _init(self, ohlc, trade_data):
        self.items_dict = {}
        self.items_dict['open'] = TradeDataScatter()
        self.items_dict['close'] = TradeDataScatter()
        self.items_dict['link_line'] = TradeDataLinkLine(pen=pg.mkPen('w', width=1))
        self.items_dict['info_text'] = pg.TextItem(anchor=(1, 1))
        self.plt.addItem(self.items_dict['open'])
        self.plt.addItem(self.items_dict['close'])
        self.plt.addItem(self.items_dict['link_line'])
        self.plt.addItem(self.items_dict['info_text'])


    # --------------------------------添加交易数据-----------------------------------------------------------------
    def _update(self, ohlc, trade_data):
        x = ohlc.x
        U = self.long_symbol
        D = self.short_symbol
        try:
            self.items_dict['open'].setData(x=x.reindex(trade_data.open.index.floor(ohlc.ktype)),
                                            y=trade_data['OpenPrice'],
                                            symbol=[U if t == 0 else D for t in trade_data['Type']],
                                            brush=trade_data['Status'].map(
                                                     {2: pg.mkBrush(QBrush(QColor(0, 0, 255))),
                                                      1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                      0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist(),
                                            size=5
                                            )
        except Exception as e:
            V_logger.error(f'初始化交易数据标记TradeDataScatter-open失败')
        try:
            self.items_dict['close'].setData(x=x.reindex(trade_data.close.index.floor(ohlc.ktype)),
                                             y=trade_data['ClosePrice'],
                                             symbol=[D if t == 0 else U for t in trade_data['Type']],
                                             brush=trade_data['Status'].map(
                                                      {2: pg.mkBrush(QBrush(QColor(255, 255, 0))),
                                                       1: pg.mkBrush(QBrush(QColor(255, 0, 255))),
                                                       0: pg.mkBrush(QBrush(QColor(255, 255, 255)))}).tolist(),
                                             size=5
                                             )
        except Exception as e:
            V_logger.error(f'初始化交易数据标记TradeDataScatter-open失败')

        # -------------------------------------------------------------------------------------------------------------
        def link_line(a, b):
            trade_data = ohlc.Trade_Data
            if a is self.items_dict['open']:
                for i, d in enumerate(self.items_dict['open'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break
            elif a is self.items_dict['close']:
                for i, d in enumerate(self.items_dict['close'].data):
                    if b[0].pos().x() == d[0] and b[0].pos().y() == d[1]:
                        index = i
                        break

            open_x = self.items_dict['open'].data[index][0]
            open_y = self.items_dict['open'].data[index][1]
            open_symbol = self.items_dict['open'].data[index][3]  # open_symbol来区别开仓平仓
            if trade_data["Status"].iloc[index] == 2:
                close_x = self.items_dict['close'].data[index][0]
                close_y = self.items_dict['close'].data[index][1]
            else:
                close_x = self.items_dict['close'].data[index][0]
                close_y = ohlc._last_tick.Price if ohlc._last_tick else ohlc.data.iloc[-1]['close']
            profit = round(close_y - open_y, 2) if open_symbol == "t1" else round(open_y - close_y, 2)
            pen_color_type = ((open_symbol == 't1') << 1) + (open_y < close_y)
            pen_color_map_dict = {0: 'r', 1: 'g', 2: 'g', 3: 'r'}
            self.items_dict['link_line'].setData([[open_x, open_y],
                                                  [close_x, close_y]],
                                                 pen_color_map_dict[pen_color_type])
            self.items_dict['info_text'].setHtml(
                f'<span style="color:white">Account:{trade_data["Account_ID"].iloc[index]}<span/><br/>'
                f'<span style="color:blue">Open :{open_y}<span/><br/>'
                f'<span style="color:yellow">Close:{close_y}<span/><br/>'
                f'<span style="color:white">Type  :{"Long" if open_symbol == "t1" else "Short"}<span/><br/>'
                f'<span style="color:{"red" if profit >=0 else "green"}">Profit:{profit}<span/><br/>'
                f'<span style="color:"white">trader:{trade_data["trader_name"].iloc[index]}<span/>')
            self.items_dict['info_text'].setPos(self.plt.getViewBox().viewRange()[0][1],
                                                self.plt.getViewBox().viewRange()[1][0])

        self.items_dict['open'].sigClicked.connect(link_line)
        self.items_dict['close'].sigClicked.connect(link_line)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)

class Graph_Slicer(graph_base):
    def __init__(self, plt):
        super(Graph_Slicer, self).__init__(plt, 'Slicer')

    def _init(self, ohlc):
        self.items_dict['close_curve'] = pg.PlotDataItem()
        self.items_dict['date_region'] = pg.LinearRegionItem([1, 100])
        self.plt.addItem(self.items_dict['close_curve'])
        self.plt.addItem(self.items_dict['date_region'])

    def _update(self, ohlc):
        self.items_dict['close_curve'].setData(ohlc.x, ohlc.close)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)

    def init(self, ohlc):
        if not self._active:
            self.items_dict = {}
            self._init(ohlc)
            V_logger.info(f'G+初始化{self.name}图表')
            self._active = True
        else:
            V_logger.error(f'G+{self.name}图表已存在')

    def update(self, ohlc):
        if self._active:
            self._update(ohlc)
            V_logger.info(f'G↑更新{self.name}图表')
        else:
            V_logger.info(f'G↑{self.name}图表未初始化')

class Graph_BuySell(graph_base):
    def __init__(self, plt, buy_symbol='t1', sell_symbol='t', buy_brush='r', sell_brush='g', size=8):
        super(Graph_BuySell, self).__init__(plt, 'BuySell')
        self.buy_symbol = buy_symbol
        self.sell_symbol = sell_symbol
        self.buy_brush = buy_brush
        self.sell_brush = sell_brush
        self.size = size

    def _init(self, ohlc, h_buysell):
        self.items_dict = {}
        self.items_dict['buy'] = pg.ScatterPlotItem()
        self.items_dict['sell'] = pg.ScatterPlotItem()
        self.plt.addItem(self.items_dict['buy'])
        self.plt.addItem(self.items_dict['sell'])


    def _update(self, ohlc, h_buysell):
        x = ohlc.x
        open = ohlc.open
        buy_index = h_buysell.buy_points.index
        sell_index = h_buysell.sell_points.index
        self.items_dict['buy'].setData(x=x[buy_index], y=open[buy_index],
                                       symbol=self.buy_symbol, brush=self.buy_brush,
                                       size=self.size)
        self.items_dict['sell'].setData(x=x[sell_index], y=open[sell_index],
                                        symbol=self.sell_symbol, brush=self.sell_brush,
                                        size=self.size)

    def _deinit(self):
        for k, v in self.items_dict.items():
            self.plt.removeItem(v)
