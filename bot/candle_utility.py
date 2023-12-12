from openfx_api.OpenFxApi import OpenFxApi
from models.candle_timing import CandleTiming


class CandleManager:

    MAIN_LOG = "main"

    def __init__(self, api: OpenFxApi, trade_settings, log_message, granularity):
        self.api = api
        self.trade_settings = trade_settings
        self.log_message = log_message
        self.granularity = granularity
        self.pairs_list = list(self.trade_settings.keys())
        self.timings = { p: CandleTiming(self.api.last_complete_candle(p, self.granularity)) for p in self.pairs_list }
        for p, t in self.timings.items():
            self.log_message(f"CandleManager() collected most recent candle: {t}", p)


    def update_timings(self):

        triggered = []

        for pair in self.pairs_list:
            latest = self.api.last_complete_candle(pair, self.granularity)
            print(f"CandleManager {pair} current:{latest} last:{self.timings[pair].last_time}")
            if latest is None:
                self.log_message(f"CandleManager: Unable to get candle for {pair}")
                continue
            self.timings[pair].is_ready = False
            if latest > self.timings[pair].last_time:
                self.timings[pair].is_ready = True
                self.timings[pair].last_time = latest
                print(f"CandleManager - {self.timings[pair]}", pair)
                triggered.append(pair)
        return triggered
