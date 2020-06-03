
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository


class IDashboardRepository(BaseRepository):
    pass


class DashboardRepository(MongoBaseRepository):
    def __init__(self, mongoclient, db, collectionName:str):
        super().__init__(mongoclient=mongoclient, db=db, collectionName=collectionName)
