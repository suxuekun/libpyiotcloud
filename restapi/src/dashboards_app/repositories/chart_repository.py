
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from dashboards_app.models.dashboard import GATEWAYS

class IChartRepository(BaseRepository, IMongoBaseRepository):
    
    def get_charts_gateways(self, dashboardId):
        pass

    
class ChartRepository(MongoBaseRepository, IChartRepository):

    def get_charts_gateways(self, dashboardId):
        query = {
            "device.type": GATEWAYS,
            "dashboardId": dashboardId
        }
        return super().gets(query)
    