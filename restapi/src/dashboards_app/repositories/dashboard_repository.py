
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository


class IDashboardRepository(BaseRepository):
    def get_summaried_dashboards(self, query=None):
        pass

class DashboardRepository(MongoBaseRepository, IDashboardRepository):
    def __init__(self, mongoclient, db, collectionName):
            super().__init__(mongoclient, db, collectionName)

    def get_summaried_dashboards(self, query=None):
        projection = {
            "sensors": 0,
            "gateways": 0,
            "actuators": 0,
        }
        cursors = self.collection.find(query, projection).sort("modifiedAt", -1)
        results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
        return results
    