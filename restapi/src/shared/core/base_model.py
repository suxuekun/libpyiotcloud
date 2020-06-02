
from datetime import datetime


class BaseModel:
    
    def __init__(self, id: str):
        self._id = id
    
    def toModel(self, id: str, data: {}):
        pass
        
class WithCreatedTimestamp:
    
    def __init__(self, createdAt: str):
        self.createdAt = createdAt

        
class WithUpdatedTimeStamp:

    def __init__(self, updatedAt: str):
        self.updatedAt = updatedAt

