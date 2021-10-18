# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy, merge_informative_pair
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import Trailing_Gain_Util

class Trailing_Gain_Profit(IStrategy):
    """
    How to use it?
    > python3 freqtrade -s Trailing_Gain_Profit
    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.10



    # Optional order type mapping
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """

        pair_tg=new Trailing_Gain_Util(pair);

        pair_tg.adjust_gain_profit(get_current_price())
        
        
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
        if self.dp:
            # Get ohlcv data for informative pair at 15m interval.
            inf_tf = '15m'
            informative = self.dp.get_pair_dataframe(pair=f"BTC/USDT",
                                                     timeframe=inf_tf)

            # calculate SMA20 on informative pair
            informative['sma20'] = informative['close'].rolling(20).mean()

            # Combine the 2 dataframe
            # This will result in a column named 'closeETH' or 'closeBTC' - depending on stake_currency.
            dataframe = merge_informative_pair(dataframe, informative,
                                               self.timeframe, inf_tf, ffill=True)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        
        dataframe.loc[
            (
                pair_tg.get_buy_flag()
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['ema20'] < dataframe['ema50']) &
                # stake/USDT below sma(stake/USDT, 20)
                (dataframe['close_15m'] < dataframe['sma20_15m'])
            ),
            'sell'] = 1
        return dataframe