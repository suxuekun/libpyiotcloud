from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository


class IMemosAlertRepository(BaseRepository, IMongoBaseRepository):
    pass

class MenosAlertRepository(MongoBaseRepository, IMemosAlertRepository):
    pass