
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import IStrategy


class ConvergeDivergenceSlope(IStrategy):
    INTERFACE_VERSION = 2
    stoploss = -0.10
    trailing_stop = True
    no_of_candles_to_con_div = 5
    no_of_candles_to_con_div_min = 3
    no_of_candles_to_con_div_max = 30
    # which_to_check='body'
    which_to_check = 'wick top'
    final_df = pd.DataFrame()

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

    def categorise(self, row):
        if self.which_to_check == 'body':
            return max(row['open'], row['close'])
        else:
            return row['high']

    def body_top(self, row):
        return max(row['open'], row['close'])

    def diverge_converge(self, row, no_of_candles_to_con_div):
        return (row['top'] - row['old_top' + '_' + str(no_of_candles_to_con_div)])

    def rsi_mov_ind(self, row, no_of_candles_to_con_div):
        return (row['rsi'] - row['old_rsi' + '_' + str(no_of_candles_to_con_div)])

    def line_eq(self, row, no_of_candles_to_con_div):
        # xpoints=[row['row_num'],row['old_row_num'+'_'+str(no_of_candles_to_con_div)]]
        # ypoints=[row['top'],row['old_top'+'_'+str(no_of_candles_to_con_div)]]

        xpoints = [row['row_num'], row['top']]
        ypoints = [row['old_row_num' + '_' + str(no_of_candles_to_con_div)],
                   row['old_top' + '_' + str(no_of_candles_to_con_div)]]
        a = ypoints[1] - xpoints[1]
        b = xpoints[0] - ypoints[0]
        c = a * (xpoints[0]) + b * (xpoints[1])
        # print("row['row_num'] =",row['row_num'])
        # print("xp = ",xpoints)
        # print("yp =",ypoints)
        # print("abc=",a,"b:",b,"c:",c)
        return {'a': a, 'b': b, 'c': c}

    def informative_pairs(self):
        return []

    def per_in_cal(self, row, no_of_candles_to_con_div):
        if row['old_rsi' + '_' + str(no_of_candles_to_con_div)]:
            return (abs(row['rsi_mov' + '_' + str(no_of_candles_to_con_div)] / row[
                'old_rsi' + '_' + str(no_of_candles_to_con_div)] * 100))
        else:
            return 0

    def per_in_cal_prc(self, row, no_of_candles_to_con_div):
        if row['old_rsi' + '_' + str(no_of_candles_to_con_div)]:
            return (abs(row['div_conv' + '_' + str(no_of_candles_to_con_div)] / row[
                'old_top' + '_' + str(no_of_candles_to_con_div)] * 100))
        else:
            return 0

    def rsi_tradingview(self, ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):

        delta = ohlc["close"].diff()

        up = delta.copy()
        up[up < 0] = 0
        up = pd.Series.ewm(up, alpha=1 / period).mean()

        down = delta.copy()
        down[down > 0] = 0
        down *= -1
        down = pd.Series.ewm(down, alpha=1 / period).mean()

        rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

        return np.round(rsi, 2) if round_rsi else rsi

    def above_or_below_line(self, row, no_of_candles_to_con_div):
        # print("row_numbers x: ", row['row_num'])
        # print("middle candles y", row['middle_candles'+'_'+str(no_of_candles_to_con_div)])
        dt = row['line_eq' + '_' + str(no_of_candles_to_con_div)]
        # print("parms: ",dt)

        xpoints = np.arange(row['row_num'] - no_of_candles_to_con_div + 1, row['row_num']) - 0.25

        yNew = (dt['c'] - (xpoints * dt['a'])) / dt['b']

        # print("ynew:",yNew)
        # print("sl:",row['middle_candles'+'_'+str(no_of_candles_to_con_div)] < yNew)
        if row['row_num'] > no_of_candles_to_con_div:
            return all(row['middle_candles' + '_' + str(no_of_candles_to_con_div)] < yNew)
        else:
            return np.nan

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe= dataframe.sort_values(by='date',ascending=True).tail(self.no_of_candles_to_con_div_max+50)
        dataframe['rsi'] = self.rsi_tradingview(dataframe)
        dataframe['p_rsi'] = dataframe['rsi'].shift(1)
        dataframe['rr'] = dataframe['rsi'] > dataframe['p_rsi']
        dataframe['top'] = dataframe.apply(lambda row: self.categorise(row), axis=1)
        dataframe['buy_tag'] = np.nan
        dataframe.insert(loc=0, column='row_num', value=np.arange(1, len(dataframe) + 1))
        for no_of_candles_to_con_div in range(self.no_of_candles_to_con_div_min, self.no_of_candles_to_con_div_max):
            dataframe['old_rsi' + '_' + str(no_of_candles_to_con_div)] = dataframe['rsi'].shift(no_of_candles_to_con_div)
            dataframe['old_row_num' + '_' + str(no_of_candles_to_con_div)] = dataframe['row_num'].shift(no_of_candles_to_con_div)
            dataframe['rsi_mov' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.rsi_mov_ind(row, no_of_candles_to_con_div), axis=1)
            dataframe['old_top' + '_' + str(no_of_candles_to_con_div)] = dataframe['top'].shift(no_of_candles_to_con_div)
            dataframe['div_conv' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.diverge_converge(row, no_of_candles_to_con_div), axis=1)
            dataframe['per_inc' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.per_in_cal(row, no_of_candles_to_con_div), axis=1)
            dataframe['per_inc_prc' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.per_in_cal_prc(row, no_of_candles_to_con_div), axis=1)

            dataframe['line_eq' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.line_eq(row, no_of_candles_to_con_div), axis=1)
            dataframe['body_top' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.body_top(row), axis=1)

            list_of_values = [np.nan]*(no_of_candles_to_con_div-1)

            dataframe['body_top' + '_' + str(no_of_candles_to_con_div)].rolling(no_of_candles_to_con_div - 1,closed='left').apply(lambda x: list_of_values.append(x.values) or np.nan, raw=False)
            # dataframe['old_row_num'+'_'+str(no_of_candles_to_con_div)].rolling(no_of_candles_to_con_div-1, closed='left').apply(lambda x: list_of_values.append(x.values) or np.nan, raw=False)
            dataframe['middle_candles' + '_' + str(no_of_candles_to_con_div)] = pd.Series(list_of_values).values

            dataframe['above_or_below_line' + '_' + str(no_of_candles_to_con_div)] = dataframe.apply(lambda row: self.above_or_below_line(row, no_of_candles_to_con_div), axis=1)

            dataframe.loc[
                (
                        (dataframe['div_conv' + '_' + str(no_of_candles_to_con_div)] > 0)
                        & (dataframe['rsi_mov' + '_' + str(no_of_candles_to_con_div)] < 0)
                        # & (dataframe['per_inc' + '_' + str(no_of_candles_to_con_div)] >= 1)
                        # & (dataframe['per_inc_prc' + '_' + str(no_of_candles_to_con_div)] >= 1)
                        # & (abs(dataframe['rsi_mov'+'_'+str(no_of_candles_to_con_div)]) >= 1)
                        & (dataframe['above_or_below_line' + '_' + str(no_of_candles_to_con_div)] == True)
                        & (dataframe['rr'] == True)
                )
                , 'buy' + '_' + str(no_of_candles_to_con_div)] = 1

            dataframe.loc[dataframe['buy' + '_' + str(no_of_candles_to_con_div)] == 1, 'buy_tag'] = dataframe[
                                                                                                        'buy_tag'].fillna(
                '') + '_len' + '_' + str(
                no_of_candles_to_con_div)  # + "RD:" + str(abs(dataframe['rsi_mov'+'_'+str(no_of_candles_to_con_div)])) +" PPD:" + str(dataframe['per_inc_prc' + '_' + str(no_of_candles_to_con_div)]) + "] ";

            list_of_columns_to_be_dropped = [
                'old_rsi' + '_' + str(no_of_candles_to_con_div),
                'rsi_mov' + '_' + str(no_of_candles_to_con_div),
                'old_top' + '_' + str(no_of_candles_to_con_div),
                'div_conv' + '_' + str(no_of_candles_to_con_div),
                'per_inc' + '_' + str(no_of_candles_to_con_div),
                'per_inc_prc' + '_' + str(no_of_candles_to_con_div),
                'above_or_below_line'+'_'+str(no_of_candles_to_con_div),
                'body_top' + '_' + str(no_of_candles_to_con_div),
                'middle_candles' + '_' + str(no_of_candles_to_con_div),
                'line_eq' + '_' + str(no_of_candles_to_con_div),
                'old_row_num' + '_' + str(no_of_candles_to_con_div),
                'buy' + '_' + str(no_of_candles_to_con_div)
            ]
            dataframe.drop(list_of_columns_to_be_dropped, axis=1, inplace=True)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe['buy_tag'].notnull(), 'buy'] = 1

        self.final_df = dataframe.loc[dataframe['buy_tag'].notnull()][['date', 'buy_tag']]
        self.final_df['pair'] = metadata['pair']
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        '''
        #debug: dd=dataframe[['date','buy_tag','rsi','p_rsi','high','rr']]
        dataframe.loc[
        (
            (dataframe['div_conv'] < 0) &  (dataframe['rsi_mov'] > 0) 
            & (dataframe['per_inc'] > 1000)# Make sure Volume is not 0
            10>20
        ),
        'sell'] = 0;
        '''
        dataframe['sell'] = np.nan
        return dataframe
