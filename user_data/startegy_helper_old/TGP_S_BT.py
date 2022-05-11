import logging
logger = logging.getLogger(__name__)

from typing import Dict
from datetime import datetime, timedelta, timezone


import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

#from user_data.strategies.Trailing_Gain_Util import Trailing_Gain_Util
#from user_data.strategies.TGP_db_backtest import Trailing_Gain_Util,init_db


class TGP_S_BT(IStrategy):
    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True
    TGP_dict={}
    config=None;
    #_last_candle_seen_per_pair: Dict[str, datetime] = {}

    # Optional order type mapping.
    order_types = {
        'buy': 'market',
        'sell': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }


    def __init__(self,config):
        self.config=config;
        #init_db(self.config['db_url']);
        super().__init__(config)
        
    @property
    def protections(self):
        return  [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 2
            }
        ]
    
    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #logger.info("in populate_indicators_maddy");
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['buy']=0;
        trailing_gain_profit_percent=self.config.get('TGP_percent');
        trailing_gain_profit=None;
        for i in range(len(dataframe)):
            current_price=dataframe.loc[i]['open'] 
            new_trailing_gain_profit=current_price + float (current_price* abs(trailing_gain_profit_percent))
            if i==0 or trailing_gain_profit is None:
                trailing_gain_profit=new_trailing_gain_profit
            else:
                if new_trailing_gain_profit<trailing_gain_profit:
                    trailing_gain_profit=new_trailing_gain_profit;
            if trailing_gain_profit is not None and trailing_gain_profit< current_price:
                dataframe.at[i,'buy']=1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = 0
        return dataframe
