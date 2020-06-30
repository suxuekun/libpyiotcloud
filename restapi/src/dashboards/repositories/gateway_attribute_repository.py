
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.base_repository import BaseRepository
from shared.core.exceptions import CreatedExeception

class IGatewayAttributeRepository(BaseRepository, IMongoBaseRepository):
    
    def gets_summary(self):
        pass
    
class GatewayAttributeRepository(MongoBaseRepository, IGatewayAttributeRepository):
    
    def __init__(self, mongoclient, db, collectionName):
        super().__init__(mongoclient, db, collectionName)
        
    def gets(self, query=None, projection=None):
        cursors = self.collection.find(query, projection)
        results = list(cursors)
        return results
    
    def gets_summary(self):
        projection = {
            "labels": 0,
            "filters": 0,
            "createdAt": 0,
            "modifiedAt": 0
        }
        return self.gets(projection=projection)