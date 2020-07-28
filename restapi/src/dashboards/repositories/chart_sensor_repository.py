
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId
from shared.core.exceptions import DeletedException


class IChartSensorRepository(BaseRepository, IMongoBaseRepository):
    def gets_charts(self, dashboardId, userId):
        pass

    def get_same_chart(self, dashboardId, deviceId):
        pass
    
    def get_chart_by_device(self, deviceId):
        pass

    def delete_many_by_dashboard(self, dashboardId):
        pass
    
    
class ChartSensorRepository(MongoBaseRepository, IChartSensorRepository):

    def get_same_chart(self, dashboardId, deviceId):
        query = {
            "deviceId": deviceId,
            "dashboardId": dashboardId
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

    
    def delete_many_by_dashboard(self, dashboardId):
        try:
            query = {
                "dashboardId": dashboardId
            }
            self.collection.delete_many(query)
            return True
        except Exception as e:
            print('get_one', e)
            raise DeletedException(str(e))
