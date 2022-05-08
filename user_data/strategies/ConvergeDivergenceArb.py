# -*- coding: utf-8 -*-
"""
Created on Sat May  7 22:41:16 2022

@author: harik
"""

import logging
logger = logging.getLogger(__name__)


import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter


class ConvergeDivergenceArb(IStrategy):
    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True
    no_of_candles_to_con_div =5;
    no_of_candles_to_con_div_min =5;
    no_of_candles_to_con_div_max =15;
    #which_to_check='body'
    which_to_check='wick top'
    final_df= pd.DataFrame()

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }
    
    def categorise(self,row):
        if self.which_to_check=='body':
            return max(row['open'],row['close'])
        else:
            return row['high']
	
    def diverge_converge(self,row,no_of_candles_to_con_div):
        return (row['top'+'_'+str(no_of_candles_to_con_div)]-row['old_top'+'_'+str(no_of_candles_to_con_div)])
       
    def rsi_mov_ind(self,row,no_of_candles_to_con_div):
        return (row['rsi']-row['old_rsi'+'_'+str(no_of_candles_to_con_div)])

    def informative_pairs(self):
        return []
    
    def per_in_cal(self,row,no_of_candles_to_con_div):
        if row['old_rsi'+'_'+str(no_of_candles_to_con_div)]:
            return (abs(row['rsi_mov'+'_'+str(no_of_candles_to_con_div)]/row['old_rsi'+'_'+str(no_of_candles_to_con_div)]*100))
        else:
            return 0
        
    def per_in_cal_prc(self,row,no_of_candles_to_con_div):
        if row['old_rsi'+'_'+str(no_of_candles_to_con_div)]:
            return (abs(row['div_conv'+'_'+str(no_of_candles_to_con_div)]/row['old_top'+'_'+str(no_of_candles_to_con_div)]*100))
        else:
            return 0
    
    def rsi_tradingview(self,ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):
        """ Implements the RSI indicator as defined by TradingView on March 15, 2021.
            The TradingView code is as follows:
            //@version=4
            study(title="Relative Strength Index", shorttitle="RSI", format=format.price, precision=2, resolution="")
            len = input(14, minval=1, title="Length")
            src = input(close, "Source", type = input.source)
            up = rma(max(change(src), 0), len)
            down = rma(-min(change(src), 0), len)
            rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
            plot(rsi, "RSI", color=#8E1599)
            band1 = hline(70, "Upper Band", color=#C0C0C0)
            band0 = hline(30, "Lower Band", color=#C0C0C0)
            fill(band1, band0, color=#9915FF, transp=90, title="Background")
        :param ohlc:
        :param period:
        :param round_rsi:
        :return: an array with the RSI indicator values
        """
    
        delta = ohlc["close"].diff()
    
        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1/period).mean()
    
        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1/period).mean()
    
        rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))
    
        return np.round(rsi, 2) if round_rsi else rsi

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = self.rsi_tradingview(dataframe)
        for no_of_candles_to_con_div in range(self.no_of_candles_to_con_div_min,self.no_of_candles_to_con_div_max):
            dataframe['old_rsi'+'_'+str(no_of_candles_to_con_div)]=dataframe['rsi'].shift(no_of_candles_to_con_div)
            dataframe['rsi_mov'+'_'+str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.rsi_mov_ind(row,no_of_candles_to_con_div), axis=1)
            dataframe['top'+'_'+str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.categorise(row), axis=1)
            dataframe['old_top'+'_'+str(no_of_candles_to_con_div)]=dataframe['top'+'_'+str(no_of_candles_to_con_div)].shift(no_of_candles_to_con_div)
            dataframe['div_conv'+'_'+str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.diverge_converge(row,no_of_candles_to_con_div), axis=1)
            dataframe['per_inc'+'_'+str(no_of_candles_to_con_div)] =dataframe.apply(lambda row: self.per_in_cal(row,no_of_candles_to_con_div), axis=1)
            dataframe['per_inc_prc'+'_'+str(no_of_candles_to_con_div)] =dataframe.apply(lambda row: self.per_in_cal_prc(row,no_of_candles_to_con_div), axis=1)
            dataframe['moun_line_cross'+'_'+str(no_of_candles_to_con_div)]=(dataframe['top'+'_'+str(no_of_candles_to_con_div)].rolling(no_of_candles_to_con_div).max() <= dataframe['top'+'_'+str(no_of_candles_to_con_div)])
            dataframe['mount_max'+'_'+str(no_of_candles_to_con_div)]=dataframe['top'+'_'+str(no_of_candles_to_con_div)].rolling(no_of_candles_to_con_div).max()
        return dataframe

    def populate_indicators2(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_indicators_maddy");
        #dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi'] = self.rsi_tradingview(dataframe)
        dataframe['old_rsi']=dataframe['rsi'].shift(self.no_of_candles_to_con_div)
        dataframe['rsi_mov'] = dataframe.apply(lambda row: self.rsi_mov_ind(row), axis=1)
        dataframe['top'] = dataframe.apply(lambda row: self.categorise(row), axis=1)
        dataframe['old_top']=dataframe['top'].shift(self.no_of_candles_to_con_div)
        dataframe['div_conv'] = dataframe.apply(lambda row: self.diverge_converge(row), axis=1)
        dataframe['per_inc'] =dataframe.apply(lambda row: self.per_in_cal(row), axis=1)
        dataframe['per_inc_prc'] =dataframe.apply(lambda row: self.per_in_cal_prc(row), axis=1)
        dataframe['moun_line_cross']=(dataframe['top'].rolling(self.no_of_candles_to_con_div).max() <= dataframe['top'])
        dataframe['mount_max']=dataframe['top'].rolling(self.no_of_candles_to_con_div).max()
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_buy_trend_maddy");
        for no_of_candles_to_con_div in range(self.no_of_candles_to_con_div_min,self.no_of_candles_to_con_div_max):
            dataframe.loc[
                (
                    (   
                        dataframe['div_conv'+'_'+str(no_of_candles_to_con_div)] > 0) & (dataframe['rsi_mov'+'_'+str(no_of_candles_to_con_div)] < 0)
                        & (dataframe['per_inc'+'_'+str(no_of_candles_to_con_div)] >= 1) & (dataframe['per_inc_prc'+'_'+str(no_of_candles_to_con_div)] >= 1)
                        & (dataframe['moun_line_cross'+'_'+str(no_of_candles_to_con_div)] == True
                    )
                )
                ,'buy'+'_'+str(no_of_candles_to_con_div)] = 1;
            if no_of_candles_to_con_div==self.no_of_candles_to_con_div_min:
                dataframe.loc[dataframe['buy'+'_'+str(no_of_candles_to_con_div)]==1,'buy_tag'] = '_len'+'_'+str(no_of_candles_to_con_div);
            else:
                dataframe.loc[dataframe['buy'+'_'+str(no_of_candles_to_con_div)]==1,'buy_tag'] = dataframe['buy_tag']+'_len'+'_'+str(no_of_candles_to_con_div);
        
        self.final_df=dataframe.loc[dataframe['buy_tag'].notnull()][['date','buy_tag']]
        self.final_df['pair']=metadata['pair']
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_sell_trend_maddy");
        '''
        dataframe.loc[
        (
            (dataframe['div_conv'] < 0) &  (dataframe['rsi_mov'] > 0) 
            & (dataframe['per_inc'] > 1000)# Make sure Volume is not 0
            10>20
        ),
        'sell'] = 0;
        '''
        dataframe['sell'] = np.nan;
        return dataframe
