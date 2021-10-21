import logging
logger = logging.getLogger(__name__)


import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

from user_data.strategies.Trailing_Gain_Util import Trailing_Gain_Util

class SampleStrategyNew(IStrategy):
    TGP_dict={}


    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True


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


    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print("in populate_indicators_maddy");
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print("in populate_buy_trend_maddy");
        if not (self.TGP_dict.get(metadata['pair']) and isinstance(self.TGP_dict.get(metadata['pair']), Trailing_Gain_Util)):
            self.TGP_dict[metadata['pair']]=Trailing_Gain_Util(self.dp._exchange,metadata['pair'],logger,0.01)
        
        
        
        tgu_obj=self.TGP_dict.get(metadata['pair']);
        """
        dataframe.loc[
            (
                (tgu_obj.get_buy_flag())  # Make sure Volume is not 0
            ),
            'buy'] = 1
        """
        if tgu_obj.get_buy_flag():
            dataframe['tgp_buy']=True;
            dataframe.loc[
            (
                (dataframe['tgp_buy'] & dataframe['volume']>0)  # Make sure Volume is not 0
            ),
            'buy'] = 1;
        else:
            dataframe['tgp_buy']=False;
            dataframe['buy'] = 0;
            
        

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        print("in populate_sell_trend_maddy");
        dataframe['sell'] = 0
        return dataframe
