
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId


class IChartSensorRepository(BaseRepository, IMongoBaseRepository):
    def gets_charts(self, dashboardId, userId):
        pass

    def get_same_chart(self, deviceId):
        pass
    
    def get_chart_by_device(self, deviceId):
        pass
    
class ChartSensorRepository(MongoBaseRepository, IChartSensorRepository):

    def get_same_chart(self, deviceId):
        query = {
            "deviceId": deviceId,
        }
        chart = self.get_one(query)
        return chart

    def gets_charts(self, dashboardId, userId):
        query = {
            'dashboardId': dashboardId,
            'userId': userId,
        }
        return super().gets(query=query)

    def get_chart_by_device(self, deviceId):
        query = {
            "deviceId": deviceId,
        }
        charts = self.gets(query)
        return charts
