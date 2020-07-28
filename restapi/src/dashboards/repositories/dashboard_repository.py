
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId
from shared.core.exceptions import CreatedExeception, DeletedException, QueriedByIdException, QueriedManyException, UpdatedException

class IDashboardRepository(BaseRepository, IMongoBaseRepository):
    def get_summaried_dashboards(self, query=None):
        pass

    def get_same_dashboard(self, dashboardName: str):
        pass
    
class DashboardRepository(MongoBaseRepository, IDashboardRepository):
    def __init__(self, mongoclient, db, collectionName):
        super().__init__(mongoclient, db, collectionName)

    def get_summaried_dashboards(self, query=None):
        try:
            cursors = self.collection.find(query).sort("modifiedAt", -1)
            results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
            return results
        except Exception as e:
            raise QueriedManyException(str(e))
    
    def get_same_dashboard(self, dashboardName):
        try:
            name = dashboardName.strip()
            query =  {
                "name": dashboardName
            }
            result = self.get_one(query)
            return result
        except Exception as e:
            raise QueriedManyException(str(e))

