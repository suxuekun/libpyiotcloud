from pymongo import MongoClient
from datetime import datetime
from .base_repository import BaseRepository
from shared.core.exceptions import CreatedExeception, DeletedException, QueriedByIdException, QueriedManyException, UpdatedException
from bson.objectid import ObjectId
from bson.json_util import dumps
from shared.utils import timestamp_util


class MongoBaseRepository(BaseRepository):

    def __init__(self, mongoclient: MongoClient, db, collectionName: str):
        self.mongoclient = mongoclient
        self.db = db
        self.collectionName = collectionName
        self.collection = db[collectionName]

    def check_collection_existed(self):
        return self.collectionName in self.db.list_collection_names()

    def create(self, input) -> str:
        try:
            if "_id" in input:
                input.pop("_id")
                
            res = self.collection.insert_one(input)
            return res.inserted_id
        except Exception as e:
            print(e)
            raise CreatedExeception(str(e))

    def update(self, id: str, input) -> bool:
        try:
            query = {
                "_id": ObjectId(id)
            }
            if input["_id"] is not None:
                input.pop("_id")
                
            input["modifiedAt"] = timestamp_util.get_timestamp()
            self.collection.update_one(query, {"$set": input})
            return True
        
        except Exception as e:
            print(e)
            raise UpdatedException(str(e))

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
            raise QueriedByIdException(str(e))

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
                "_id": ObjectId(id)
            }
            self.collection.delete_one(query)
            return True
        except Exception as e:
            print(e)
            raise DeletedException(str(e))
        

