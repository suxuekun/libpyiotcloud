
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from datetime import datetime, timezone

class ISensorRepository(BaseRepository, IMongoBaseRepository):
    pass

class SensorRepository(MongoBaseRepository, ISensorRepository):
    pass
