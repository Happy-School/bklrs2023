from openfx_api.OpenFxApi import OpenFxApi
from openfx_api.NewsApi import AlphaVantageApi
from infrastructure.instrument_collection import instrumentCollection

if __name__ == '__main__':
    api = OpenFxApi()
    n_api = AlphaVantageApi()
    print(api.get_candles_df(pair_name="EURUSD", count=-32, granularity="M1"))