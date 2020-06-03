
from pymongo import MongoClient  # MongoDB


class CachedMongoClientService:
    __instance = None
    __mongoClient = None

    @staticmethod
    def get_instacne():
        if CachedMongoClientService.__instance == None:
            CachedMongoClientService()
        return CachedMongoClientService.__instance

    def __init__(self):
        if CachedMongoClientService.__instance == None:
            CachedMongoClientService.__instance = self

    def set_mongo_client(self, mongoClient):
        self.__mongoClient = mongoClient

    def get_mongo_client(self):
        return self.__mongoClient
    