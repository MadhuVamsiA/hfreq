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
from user_data.strategies.TGP_db import Trailing_Gain_Util,init_db


class TGP_S(IStrategy):
    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True
    TGP_dict={}
    config=None;
    _last_candle_seen_per_pair: Dict[str, datetime] = {}

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
        init_db(self.config['db_url']);
        
    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        logger.info("in populate_indicators_maddy");
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if self.config.get('trailing_gain_on'):
            tgu_obj=Trailing_Gain_Util.query.filter(Trailing_Gain_Util.pair == metadata['pair']).one_or_none()
            if tgu_obj is None:
                tgu_obj=Trailing_Gain_Util(self.dp._exchange,metadata['pair'],self.config.get('TGP_percent'));
                Trailing_Gain_Util.query.session.add(tgu_obj);
                Trailing_Gain_Util.commit();


            if tgu_obj.get_buy_flag(self.dp._exchange):
                dataframe['tgp_buy']=True;
                dataframe.loc[
                (
                    (dataframe['tgp_buy'] & dataframe['volume']>0)  # Make sure Volume is not 0
                ),
                'buy'] = 1;
            else:
                dataframe['tgp_buy']=False;
                dataframe['buy'] = 0;
                
        else:
            logger.info("TGP is off");
            dataframe['buy'] = 0;

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['sell'] = 0
        return dataframe
