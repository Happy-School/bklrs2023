from infrastructure.instrument_collection import instrumentCollection as ic
from openfx_api.OpenFxApi import OpenFxApi
import pandas as pd

def print_beautiful_df(df):
    pd.set_option('display.max_rows', None)  
    pd.set_option('display.max_columns', None)  
    pd.set_option('display.width', 1000) 
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 3)  

    df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')

    print(df)

if __name__ == "__main__":
    ic.LoadInstruments()
    api = OpenFxApi()

    df_merged = api.last_complete_candle(pair_name="EURUSD", granularity="H4")
    print (df_merged)
