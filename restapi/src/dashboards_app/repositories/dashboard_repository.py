
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository


class IDashboardRepository(BaseRepository):
    def get_summaried_dashboards(self, query=None):
        pass


class DashboardRepository(MongoBaseRepository, IDashboardRepository):
    def __init__(self, mongoclient, db, collectionName:str):
        super().__init__(mongoclient=mongoclient, db=db, collectionName=collectionName)

    
    def get_summaried_dashboards(self, query=None):
        projection = {
            "sensors": 0,
            "gateways": 0,
            "actuators": 0,
            "createdAt": 0,
            "modifiedAt": 0
        }
        return super().gets(query, projection)