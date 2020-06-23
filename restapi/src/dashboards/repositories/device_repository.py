
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository

class IDeviceRepostory(BaseRepository, IMongoBaseRepository):
    
    def get_by_uuid(self, uuid):
        pass
    
class DeviceRepository(MongoBaseRepository, IDeviceRepostory):
    
    def get_by_uuid(self, uuid):
        query = {
            "deviceid": uuid
        }
        return super().get_one(query) 
    