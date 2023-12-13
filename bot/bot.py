import time
from bot.candle_utility import CandleManager
from bot.trade_analysis import TradeProcessor
from bot.trade_execution import place_trade
from infrastructure.log_wrapper import LogWrapper
from infrastructure.db.mongoDb import MongoDB
from models.trade_settings import TradeSettings
from openfx_api.OpenFxApi import OpenFxApi
import constants.defs as defs

class TradingBot:

    ERROR_LOGGER = "error"
    MAIN_LOGGER = "main"
    TIMEFRAME = "M1"
    SLEEP_INTERVAL = 7

    def __init__(self):
        self.load_pair_settings()
        self.initialize_logging()
        self.api = OpenFxApi()
        self.candle_manager = CandleManager(self.api, self.trade_configs, self.log_message, TradingBot.TIMEFRAME)
        self.trade_processor = TradeProcessor(self.log_message)
        self.is_running = True

    def load_pair_settings(self):
        
        self.mongo = MongoDB()
        MONGO_COLLECTION = "Settings"  # Adjust as needed        
        config_data = self.mongo.find_one(MONGO_COLLECTION)

        if config_data:
            self.trade_configs = {
                pair: TradeSettings(value) for pair, value in config_data.get('pairs', {}).items()
            }
            self.trade_risk = config_data.get('trade_risk')
        else:
            self.trade_configs = {}
            self.trade_risk = 0
        
        self.mongo.close_connection()

    def initialize_logging(self, add_logs_for_pairs=True):
        self.logs = {}
        
        def add_log_for_pair(pair_name, trade_config):
            self.logs[pair_name] = LogWrapper(pair_name)
            self.log_message(f"Setting up trade settings for {trade_config}", pair_name)

        if add_logs_for_pairs:
            for pair_name, trade_config in self.trade_configs.items():
                add_log_for_pair(pair_name, trade_config)
        
        self.add_default_loggers()

    def add_default_loggers(self):
        for log_name in [TradingBot.ERROR_LOGGER, TradingBot.MAIN_LOGGER]:
            self.logs[log_name] = LogWrapper(log_name)
        self.log_to_main(f"Trading Bot initialized with settings: {TradeSettings.settings_to_str(self.trade_configs)}")


    def log_message(self, msg, key):
        self.logs[key].logger.debug(msg)

    def log_to_main(self, msg):
        self.log_message(msg, TradingBot.MAIN_LOGGER)

    def log_to_error(self, msg):
        self.log_message(msg, TradingBot.ERROR_LOGGER)

    def trade_execution(self, triggered_pairs):
        if triggered_pairs:
            self.log_message(f"Processing triggered pairs: {triggered_pairs}", TradingBot.MAIN_LOGGER)
            for pair in triggered_pairs:
                last_candle_time = self.candle_manager.timings[pair].last_time
                applied_trade_decision = self.trade_processor.analyze_trade_decision(last_candle_time, pair, TradingBot.TIMEFRAME, self.api,
                                                    self.trade_configs[pair], self.log_message)
                if applied_trade_decision is not None and applied_trade_decision.signal != defs.NONE: 
                    self.log_message(f"Placing trade: {applied_trade_decision }", pair)
                    self.log_to_main(f"Placing trade: {applied_trade_decision}")
                    place_trade(applied_trade_decision, self.api, self.log_message, self.log_to_error, self.trade_risk)

    def turn_on_bot(self):
        self.is_running = True
        self.log_to_main("Bot turned on")
        self.run_bot()

    def shutdown_bot(self):
        self.log_to_main("Bot shut down")
        
    def run_bot(self):
        while self.is_running:
            time.sleep(TradingBot.SLEEP_INTERVAL)
            try:
                triggered_pairs = self.candle_manager.update_timings()
                self.trade_execution(triggered_pairs)
            except Exception as error:
                self.log_to_error(f"Trading Bot CRASH: {error}")
                break
