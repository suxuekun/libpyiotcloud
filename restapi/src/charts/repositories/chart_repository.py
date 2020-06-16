
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId

class IChartRepository(BaseRepository, IMongoBaseRepository):
    
    def get_charts_gateways(self, dashboardId):
        pass
    
    def get_detail(self, dashboarId, chartId):
        pass
    
class ChartRepository(MongoBaseRepository, IChartRepository):

    def get_charts_gateways(self, dashboardId):
        query = {
            "device.type": "GATEWAYS",
            "dashboardId": dashboardId
        }
        return super().gets(query)
    
    def get_detail(self, dashboarId, chartId):
        query = {
            "_id": ObjectId(chartId),
            "dashboardId": dashboarId
        }
        return super().get_one(query)
    