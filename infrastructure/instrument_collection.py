from models.instrument import Instrument
from infrastructure.db.mongoDb import MongoDB

class InstrumentCollection:
    API_KEYS = ['Symbol', 'Precision', 'TradeAmountStep']

    def __init__(self):
        self.instruments_dict = {}

        
    def LoadInstruments(self):
        self.instruments_dict = {}
        MONGO_COLLECTION = "Instruments"
        data = MongoDB().find_one(MONGO_COLLECTION)
        if data is not None:
            for k, v in data.items():
                if k != '_id':
                    self.instruments_dict[k] = Instrument.FromApiObject(v)
        else:
            print(f"No documents found in {MONGO_COLLECTION}")

    def CreateMongoDb(self, data):
        if data is None:
            print("No instrument data")
            return
        
        instruments_dict = {}
        for i in data:
            key = i['Symbol']
            instruments_dict[key] = { k: i[k] for k in self.API_KEYS }
        
        db = MongoDB()
        MONGO_COLLECTION = "Instruments"
        db.delete_many(MONGO_COLLECTION)
        db.insert_one(MONGO_COLLECTION, instruments_dict)
            

    def PrintInstruments(self):
        [print(k,v) for k,v in self.instruments_dict.items()]
        print(len(self.instruments_dict.keys()), "instruments")

instrumentCollection = InstrumentCollection()
