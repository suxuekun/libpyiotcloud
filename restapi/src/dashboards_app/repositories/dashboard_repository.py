
from ...shared.core.mongo_base_repository import MongoBaseRepository

class DashboardRepository(MongoBaseRepository[Dashboard]):
    def __init__(self, mongoclient=None, collection=''):
        super().__init__( mongoclient=mongoclient, collection=collection)