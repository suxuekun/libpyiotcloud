
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from datetime import datetime, timezone

class ISensorRepository(BaseRepository, IMongoBaseRepository):
    def get_by_source_and_number(self, source: str, number:str):
        pass

class SensorRepository(MongoBaseRepository, ISensorRepository):
    
    
    def get_by_source_and_number(self, source, number):
        query = {
            "source": source,
            "number": number
        }

        return super().get_one(query)
