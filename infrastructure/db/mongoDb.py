from pymongo import MongoClient
from constants.defs import MONGO_CONN

class MongoDB:
    def __init__(self):
        self.client = MongoClient(MONGO_CONN)
        self.db = self.client.BackOffice
    
    def test_connection(self):
        print(self.db.list_collection_names())

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find(self, collection_name, query={}):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def find_one(self, collection_name, query={}):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update)

    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)
    
    def delete_many(self, collection_name, query={}):
        collection = self.get_collection(collection_name)
        return collection.delete_many(query)


    def close_connection(self):
        self.client.close()
