from shared.core.mongo_base_repository import MongoBaseRepository


class SimpleMongoBaseRepository(MongoBaseRepository):
    def __init__(self, iotdb , collectionName:str):
        self.iotdb = iotdb
        super().__init__(mongoclient=iotdb.conn, db=iotdb.db, collectionName=collectionName)