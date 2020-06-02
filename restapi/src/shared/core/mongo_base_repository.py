from typing import TypeVar, Generic
from pymongo import MongoClient
from datetime import datetime
from .entity import Entity
from .base_repository import BaseRepository

TypeEntity = TypeVar('TypeEntity', bound=Entity)


class MongoBaseRepository(BaseRepository[TypeEntity]):

    def __init__(self, host: str = "", port: int = -1, database: str = "",  mongoclient: MongoClient = None, collection: str = ""):

        if mongoclient == None:
            self.mongoclient = MongoClient(host, port)

        self.mongoclient = mongoclient
        self.collection = mongoclient[collection]

    def __init__(self, mongoclient: MongoClient):
        self.mongo_client = mongoclient

    def create(self, input: TypeEntity) -> bool:
        try:
            decodedObject = vars(input)
            self.collection.insert_one(decodedObject)
            return True
        except Exception as e:
            print(e)
            return False

    def update(self, id: str, input: TypeEntity) -> bool:
        try:
            query = {
                "_id": id
            }
            decodedObject = vars(input)
            decodedObject["updatedAt"] = str(datetime().utcnow().timestamp())
            self.collection.update_one(query, decodedObject)
            return True
        except Exception as e:
            print(e)
            return False

    def getById(self, id: str) -> TypeEntity:
        query = {
            "_id": id
        }
        result = self.collection.findOne(query)
        return result

    def gets(self, query, projection) -> List[TypeEntity]:
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
