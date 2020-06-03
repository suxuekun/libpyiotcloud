from pymongo import MongoClient
from datetime import datetime
from .base_repository import BaseRepository


class MongoBaseRepository(BaseRepository):

    def __init__(self, host: str = None, port: int = -1, database: str = None, mongoclient: MongoClient = None, collection: str = None):

        if mongoclient == None:
            self.mongoclient = MongoClient(host, port)

        self.mongoclient = mongoclient
        self.collection = mongoclient[collection]

    def __init__(self, mongoclient: MongoClient):
        self.mongo_client = mongoclient

    def create(self, input) -> bool:
        try:
            decodedObject = vars(input)
            self.collection.insert_one(decodedObject)
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, id: str, input) -> bool:
        try:
            query = {
                "_id": id
            }
            decodedObject = vars(input)
            self.collection.update_one(query, decodedObject)
            return True
        except Exception as e:
            print(e)
            return False

    def getById(self, id: str):
        query = {
            "_id": id
        }
        result = self.collection.findOne(query)
        return result

    def gets(self, query, projection) -> []:
        results = self.collection.find(query, projection)
        return results

    def delete(self, id: str) -> bool:
        try:
            query = {
                "_id": id
            }
            self.collection.delete_one(query)
            return True
        except Exception as e:
            print(e)
            return False
