import datetime as dt

class CandleTiming:

    def __init__(self, last_time):
        self.last_time = last_time
        self.is_ready = False

    def __repr__(self):
        return f"collected most recent candle: {dt.datetime.strftime(self.last_time, '%y-%m-%d %H:%M')} Is-ready:{self.is_ready}"