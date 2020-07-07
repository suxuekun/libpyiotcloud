
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId


class IChartRepository(BaseRepository, IMongoBaseRepository):

    def get_charts_gateway(self, dashboardId, userId):
        pass
    
    def get_charts_sensor(self, dashboardId, userId):
        pass

    def get_detail(self, dashboardId, userId, chartId, query: {}):
        pass
    
    def get_same_chart_gateway(self, dashboardId, deviceId, attributeId, chartTypeId):
        pass
    
    def get_chart_by_device(self, deviceId):
        pass
    
class ChartRepository(MongoBaseRepository, IChartRepository):

    def get_charts_sensor(self, dashboardId, userId):
        query = {
            'dashboardId': dashboardId,
            'userId': userId,
            'type': "SENSORS"
        }
        return super().gets(query=query)

    def get_charts_gateway(self, dashboardId, userId):

        pipeline = [
            {
                "$match": {
                    'dashboardId': dashboardId,
                    'userId': userId,
                    "type": "GATEWAYS"
                },
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "deviceId",
                    "foreignField": "deviceid",
                    "as": "device_info"
                }
            },
            {
                "$unwind": {
                    'path': '$device_info',
                    "preserveNullAndEmptyArrays": True 
                }
            },
            {
                "$project" : {
                    '_id': 1,
                    'userId' : 1, 
                    'dashboardId' : 1,
                    'chartTypeId': 1,
                    'attributeId': 1,
                    'device_info': 1
                }
            }
        ]
        cursors = self.collection.aggregate(pipeline)
        results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
        return results

    def get_detail(self, dashboardId, userId, chartId, queyr: {}):
        pipeline = [
            {
                "$match": {
                    'dashboardId': dashboardId,
                    '_id': ObjectId(chartId),
                    'userId': userId
                },
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "deviceId",
                    "foreignField": "deviceid",
                    "as": "device_info"
                }
            },
            {
                "$sort": {
                    "createdAt": -1
                }
            },
            {
                "$unwind": {
                    'path': '$device_info',
                     "preserveNullAndEmptyArrays": True 
                }
            },
            {
                "$project" : {
                    '_id': 1,
                    'userId' : 1, 
                    'dashboardId' : 1,
                    'chartTypeId': 1,
                    'attributeId': 1,
                    'device_info': 1
                }
            }
           
        ]
        cursors = self.collection.aggregate(pipeline)
        results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
        return results[0]
    
    def get_same_chart_gateway(self, dashboardId, deviceId, attributeId, chartTypeId):
        query = {
            "dashboardId": dashboardId,
            "deviceId": deviceId,
            "attributeId": attributeId,
            "chartTypeId": chartTypeId
        }
        
        chart = self.get_one(query)
        
        return chart

    def get_chart_by_device(self, deviceId):
        query = {
            "deviceId": deviceId,
        }
        charts = self.gets(query)
        return charts
