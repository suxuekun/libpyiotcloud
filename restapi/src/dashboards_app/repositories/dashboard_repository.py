
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository

class IDashboardRepository(BaseRepository):
    def getChartType():
        pass


class DashboardRepository(MongoBaseRepository, IDashboardRepository):
    def __init__(self, mongoclient=None, collection=''):
        super().__init__( mongoclient=mongoclient, collection=collection)
    