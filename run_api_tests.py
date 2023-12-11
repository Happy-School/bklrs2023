from infrastructure.instrument_collection import instrumentCollection
#from api.web_options import get_options
from openfx_api.OpenFxApi import OpenFxApi

from dateutil.parser import parse

import time
import constants.defs as defs

if __name__ == "__main__":
    #instrumentCollection.LoadInstrumentsDB()
    api = OpenFxApi()

    #print("\nweb options:")
    #print(get_options())

    #print("\nget_account_summary():")
    #print(api.get_account_summary())

    #print(api.get_account_instruments())

    #instruments = api.get_account_instruments()
    #print(instruments)
    #instrumentCollection.CreateFile(instruments, "./data")
    instrumentCollection.LoadInstruments("./data")
    #print(instrumentCollection.instruments_dict)
    #instrumentCollection.PrintInstruments()
    
    
    #print("\nget_candles_df():")
    #print(api.get_candles_df(pair_name="EUR_USD", count=10))

    #print(api.get_candles_df(pair_name="EURUSD", count=-10, granularity="H1"))
    #print(api.get_candles_df(pair_name="EURUSD", count=10, granularity="H1", date_f=parse("2021-01-10T00:00:00")))
    print(api.last_complete_candle(pair_name="EURUSD", granularity="H1"))

    #api.place_trade("EURUSD", 17000, defs.BUY, 1.06400, 1.06800)