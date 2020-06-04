from pymongo import MongoClient
from datetime import datetime
from .base_repository import BaseRepository
from shared.core.exceptions import CreatedExeception, DeletedException, QueriedByIdException, QueriedManyException, UpdatedException
from bson.objectid import ObjectId
from bson.json_util import dumps

class MongoBaseRepository(BaseRepository):

    def __init__(self, mongoclient: MongoClient, db, collectionName: str):
        self.mongoclient = mongoclient
        self.db = db
        self.collection = db[collectionName]

    def create(self, input) -> bool:
        try:
            self.collection.insert_one(input)
            return True
        except Exception as e:
            raise CreatedExeception(e.message)

    def update(self, id: str, input) -> bool:
        try:
            query = {
                "_id": ObjectId(id)
            }
            print("Update")
            print(input)
            self.collection.update_one(query, {"$set": input})
            return True
        except Exception as e:
            print("Update failed")
            print(e)
            raise UpdatedException(e.message)

    def getById(self, id: str):
        try:
            query = {
                "_id": ObjectId(id)
            }
            result = self.collection.find_one(query)
            result["_id"] = str(result["_id"])
            return result
        except Exception as e:
            print(e)
            raise QueriedByIdException(e.message)

    def _cast_object_without_objectId(self, data):
        data["_id"] = str(data["_id"])
        return data
    
    def gets(self, query=None, projection=None):
        cursors = self.collection.find(query, projection)
        results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
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
            raise DeletedException(e.message)
