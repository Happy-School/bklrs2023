from bot.bot import TradingBot
from infrastructure.instrument_collection import instrumentCollection

if __name__ == "__main__":
    instrumentCollection.LoadInstruments()
    t_bot = TradingBot()
    t_bot.run_bot()