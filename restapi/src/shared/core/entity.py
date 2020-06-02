
from datetime import datetime

class Entity:
    createdAt: str
    updatedAt: str
    def __init__(self, id: str):
        self._id = id
        self.createdAt = str(datetime().utcnow().timestamp())
        self.updatedAt = self.createdAt

