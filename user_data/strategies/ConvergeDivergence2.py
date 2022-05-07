import logging
logger = logging.getLogger(__name__)


import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter


class ConvergeDivergence2(IStrategy):
    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True
    no_of_candles_to_con_div =15;


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
        return max(row['open'],row['close'])
	
    def diverge_converge(self,row):
        return (row['top']-row['old_top'])
       
    def rsi_mov_ind(self,row):
        return (row['rsi']-row['old_rsi'])

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_indicators_maddy");
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi_ema'] = ta.EMA(dataframe, timeperiod=14, price='rsi')
        dataframe['old_rsi']=dataframe['rsi_ema'].shift(-self.no_of_candles_to_con_div)
        dataframe['rsi_mov'] = dataframe.apply(lambda row: self.rsi_mov_ind(row), axis=1)
        dataframe['top'] = dataframe.apply(lambda row: self.categorise(row), axis=1)
        dataframe['old_top']=dataframe['top'].shift(-self.no_of_candles_to_con_div)
        dataframe['div_conv'] = dataframe.apply(lambda row: self.diverge_converge(row), axis=1)
        dataframe['ema_open_21'] = ta.EMA(dataframe, timeperiod=21, price='open')
        dataframe['ema_open_50'] = ta.EMA(dataframe, timeperiod=50, price='open')
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_buy_trend_maddy");
        dataframe.loc[
            (
                (
                    dataframe['div_conv'] > 0) & (dataframe['rsi_mov'] < 0) & (dataframe['ema_open_21'] > dataframe['ema_open_50'])
                )
            ,'buy'] = 1;
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("in populate_sell_trend_maddy");
        dataframe.loc[
        (
            (dataframe['div_conv'] < 0) &  (dataframe['rsi_mov'] > 0) #& (dataframe['rsi'] > 60)  
            & (dataframe['ema_open_21'] < dataframe['ema_open_50']) # Make sure Volume is not 0
        ),
        'sell'] = 1;
        return dataframe
