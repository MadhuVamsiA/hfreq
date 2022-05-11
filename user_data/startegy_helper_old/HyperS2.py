from pandas import DataFrame
from functools import reduce

import talib.abstract as ta

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter, 
                                IStrategy, IntParameter)
import freqtrade.vendor.qtpylib.indicators as qtpylib

class HyperS2(IStrategy):

    minimal_roi = {
        0: 1.0
    }
    buy_adx = DecimalParameter(20, 40, decimals=1, default=30.1, space="buy")
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    buy_adx_enabled = BooleanParameter(default=True, space="buy")
    buy_rsi_enabled = CategoricalParameter([True, False], default=False, space="buy")
 
 
    sell_adx = DecimalParameter(65, 100, decimals=1, default=65.1, space="sell")
    sell_rsi = IntParameter(60, 100, default=60, space="sell")
    sell_adx_enabled = BooleanParameter(default=True, space="sell")
    sell_rsi_enabled = CategoricalParameter([True, False], default=False, space="sell")
    
    stoploss = -0.05
    timeframe = '15m'
    # Define the parameter spaces
    
        
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Generate all indicators used by the strategy
        """
        dataframe['adx'] = ta.ADX(dataframe)
        dataframe['rsi'] = ta.RSI(dataframe)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']
        
        dataframe['minus_di'] = ta.MINUS_DI(dataframe)
        dataframe['plus_di'] = ta.PLUS_DI(dataframe)
        
        # Calculate all ema_short values
        for val in self.buy_ema_short.range:
            dataframe[f'ema_short_{val}'] = ta.EMA(dataframe, timeperiod=val)

        # Calculate all ema_long values
        for val in self.buy_ema_long.range:
            dataframe[f'ema_long_{val}'] = ta.EMA(dataframe, timeperiod=val)
            
        return dataframe
        
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # GUARDS AND TRENDS
        if self.buy_adx_enabled.value:
            conditions.append(dataframe['adx'] > self.buy_adx.value)
        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] < self.buy_rsi.value)

        # TRIGGERS
        if self.buy_trigger.value == 'bb_lower':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband'])
        if self.buy_trigger.value == 'macd_cross_signal':
            conditions.append(qtpylib.crossed_above(
                dataframe['macd'], dataframe['macdsignal']
            ))
        
        conditions.append(qtpylib.crossed_above(
                dataframe['plus_di'], dataframe['minus_di']
            ))

        # Check that volume is not 0
        conditions.append(dataframe['volume'] > 0)

        conditions.append(qtpylib.crossed_above(
                dataframe[f'ema_short_{self.buy_ema_short.value}'], dataframe[f'ema_long_{self.buy_ema_long.value}']
            ))
            
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1

        return dataframe
        
        

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        conditions.append(qtpylib.crossed_above(
                dataframe[f'ema_long_{self.buy_ema_long.value}'], dataframe[f'ema_short_{self.buy_ema_short.value}']
            ))
        
        if self.sell_adx_enabled.value:
            conditions.append(dataframe['adx'] < self.sell_adx.value)
        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi.value)
            
        # Check that volume is not 0
        conditions.append(dataframe['volume'] > 0)
        
        conditions.append(qtpylib.crossed_above(
                dataframe['minus_di'], dataframe['plus_di']
            ))

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1
        return dataframe