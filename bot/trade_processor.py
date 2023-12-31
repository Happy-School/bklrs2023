import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)

from models.trade_decision import TradeDecision
from technicals.indicators import BollingerBands, add_EMA
from openfx_api.OpenFxApi import OpenFxApi
from models.trade_settings import TradeSettings
import constants.defs as defs


class TradeProcessor:

    MAIN_LOG = "main"
    ERROR_LOG = "error"
    
    def __init__(self, log_message):
        self.ADDROWS = 20
        self.log_message = log_message

    def log_to_main(self, msg):
        self.log_message(msg, TradeProcessor.MAIN_LOG)

    def log_to_error(self, msg):
        self.log_message(msg, TradeProcessor.ERROR_LOG)

    def apply_signal(self, row, trade_settings: TradeSettings):
        ema_column = f'EMA_{trade_settings.n_ma}'  

        conditions = (
            row.SPREAD <= trade_settings.maxspread and 
            row.GAIN >= trade_settings.mingain
        )

        if conditions:
            if row.mid_c > row[ema_column]:
                return defs.BUY
            elif row.mid_c < row[ema_column]: 
                return defs.SELL

        return defs.NONE


    def apply_SL_TP(self, row, trade_settings: TradeSettings):
        if row.SIGNAL == defs.BUY:
            return row.mid_c - (row.GAIN / trade_settings.riskreward), row.mid_c + row.GAIN
        elif row.SIGNAL == defs.SELL:
            return row.mid_c + (row.GAIN / trade_settings.riskreward), row.mid_c - row.GAIN
        return 0.0, 0.0

    def process_candles(self, df: pd.DataFrame, pair, trade_settings: TradeSettings, log_message):
        df = df.reset_index(drop=True)
        df['PAIR'] = pair
        df['SPREAD'] = df.ask_c - df.bid_c
        df = add_EMA(df, trade_settings.n_ma, column='mid_c')
        df = BollingerBands(df, trade_settings.n_ma, trade_settings.n_std)
        df['GAIN'] = abs(df.mid_c - df.BB_MA)
        df['SIGNAL'] = df.apply(lambda row: self.apply_signal(row, trade_settings), axis=1)
        df[['SL', 'TP']] = df.apply(self.apply_SL_TP, axis=1, result_type='expand', trade_settings=trade_settings)
        df['LOSS'] = abs(df.mid_c - df.SL)

        log_cols = ['PAIR', 'time', 'SL', 'TP','GAIN', 'LOSS', 'SIGNAL']
        last_entries = df[log_cols].tail(1)
        for index, row in last_entries.iterrows():
            log_message = ",".join(f"{col}: [{row[col]}]" for col in log_cols)
            self.log_to_main(f"Processed Information - {log_message}")

        return df[log_cols].iloc[-1]

    def get_candles(self, pair, row_count, candle_time, granularity, api: OpenFxApi, log_message):
        df = api.get_candles_df(pair, count=row_count, granularity=granularity)

        if df is None or df.shape[0] == 0:
            self.log_to_error(f"Failed to retrieve candle data for {pair} in the get_candles No candles were obtained.")
            return None

        if df.iloc[-1].time != candle_time:
            self.log_to_error(f"trade_analysis -> get_candles {df.iloc[-1].time} not correct, {pair}")
            return None

        return df

    def calculate_max_candle_rows_to_get(self, trade_settings, additional_rows_to_get):
        max_candle_rows = (trade_settings.n_ma + additional_rows_to_get) * -1
        return max_candle_rows

    def analyze_trade_decision(self, candle_time, pair, granularity, api, trade_settings, log_message):
        max_candle_rows_to_get = self.calculate_max_candle_rows_to_get(trade_settings, self.ADDROWS)
        self.log_to_main(f"Analyzing trade decision: timeframe:{granularity}, {pair} candle_time:{candle_time} ")

        candle_data = self.get_candles(pair, max_candle_rows_to_get, candle_time, granularity, api, log_message)

        if candle_data is not None:
            last_processed_candle = self.process_candles(candle_data, pair, trade_settings, log_message)
            return TradeDecision(last_processed_candle)

        return None

