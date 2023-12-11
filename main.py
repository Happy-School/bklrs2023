from openfx_api.OpenFxApi import OpenFxApi
from openfx_api.NewsApi import AlphaVantageApi
from infrastructure.instrument_collection import instrumentCollection

if __name__ == '__main__':
    api = OpenFxApi()
    n_api = AlphaVantageApi()
    #instrumentCollection.LoadInstruments()
    #print(instrumentCollection.instruments_dict)
    #print(n_api.get_alpha_vantage_data())