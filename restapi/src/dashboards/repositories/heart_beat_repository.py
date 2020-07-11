
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository

class IHeartBeatRepository(BaseRepository, IMongoBaseRepository):

    def gets_by_gatewayId(self, gatewaysUUID: [], timestamp: int):
        pass

class HeartBeatRepository(MongoBaseRepository, IHeartBeatRepository):

    def gets_by_gatewayId(self, gatewaysUUID, timestamp):
        return super().gets_by_gatewayId(gatewaysUUID, timestamp)