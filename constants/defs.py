import os
from dotenv import load_dotenv
load_dotenv()
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
MONGO_CONN = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.eueawv2.mongodb.net/?retryWrites=true&w=majority"

SELL = -1
BUY = 1
NONE = 0


TFS = {
   "M5": 300,
   "M15": 900,
   "H1": 3600,
   "D": 86400
}
