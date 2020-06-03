




class CachedMongoClient:
    __instance = None
    __mongoClient = None
    __db = None

    @staticmethod
    def get_instance():
        if CachedMongoClient.__instance == None:
            CachedMongoClient()
        return CachedMongoClient.__instance
    
    def __init__(self):
        if CachedMongoClient.__instance == None:
            CachedMongoClient.__instance = self

    def set_mongo_client(self, mongoClient):
        self.__mongoClient = mongoClient

    def get_mongo_client(self):
        return self.__mongoClient

    def set_db(self, db):
        self.__db = db
    
    def get_db(self):
        return self.__db