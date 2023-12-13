import pandas as pd

def BollingerBands(df: pd.DataFrame, n=20, s=2):
    typical_p = ( df.mid_c + df.mid_h + df.mid_l ) / 3
    stddev = typical_p.rolling(window=n).std()
    df['BB_MA'] = typical_p.rolling(window=n).mean()
    df['BB_UP'] = df['BB_MA'] + stddev * s
    df['BB_LW'] = df['BB_MA'] - stddev * s
    return df


def add_EMA(df: pd.DataFrame, n=20, column='mid_c'):
    ema_column_name = f'EMA_{n}'
    df[ema_column_name] = df[column].ewm(span=n, adjust=False).mean()
    return df


























