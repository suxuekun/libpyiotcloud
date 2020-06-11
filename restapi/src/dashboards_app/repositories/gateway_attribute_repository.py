
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.base_repository import BaseRepository
from shared.core.exceptions import CreatedExeception

class IGatewayAttributeRepository(BaseRepository, IMongoBaseRepository):
    def create_many(self, inputs):
        pass
    
    def gets_summary(self):
        pass
    
class GatewayAttributeRepository(MongoBaseRepository, IGatewayAttributeRepository):
    
    def __init__(self, mongoclient, db, collectionName):
        super().__init__(mongoclient, db, collectionName)
        
    def create_many(self, inputs):
        try:
            for input in inputs:
                input.pop("_id")
            
            result = self.collection.insert_many(inputs)
            return True
        except Exception as e:
            print(e)
            raise CreatedExeception(str(e))
    
    def gets_summary(self):
        projection = {
            "lables": 0,
            "filters": 0,
            "createdAt": 0,
            "modifiedAt": 0
        }
        return super().gets(projection=projection)