from dateutil import parser

class OpenTrade:

    def __init__(self, api_ob):
        self.id = api_ob['Id']
        self.instrument = api_ob['Symbol']
        self.price = api_ob['Price']
        self.initialAmount = api_ob['InitialAmount']
        self.unrealizedPL = api_ob['Profit']
        self.marginUsed = api_ob['Margin']
        self.stop_loss = 0.0000
        self.take_profit = 0.0000
        if "StopLoss" in api_ob:
            self.stop_loss = api_ob['StopLoss']
        if "TakeProfit" in api_ob:
            self.stop_loss = api_ob['TakeProfit']

    def to_json(self):
        return {
            'id': self.id,
            'instrument': self.instrument,
            'price': self.price,
            'initialAmount': self.initialAmount,
            'unrealizedPL': self.unrealizedPL,
            'marginUsed': self.marginUsed,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }

    def __repr__(self):
        return str(vars(self))