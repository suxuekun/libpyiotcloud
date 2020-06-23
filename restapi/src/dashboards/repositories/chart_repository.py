
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from bson.objectid import ObjectId


class IChartRepository(BaseRepository, IMongoBaseRepository):

    def get_charts(self, dashboardId, userId):
        pass

    def get_detail(self, dashboarId, userId, chartId, query: {}):
        pass


class ChartRepository(MongoBaseRepository, IChartRepository):

    def get_charts(self, dashboardId, userId):

        pipeline = [
            {
                "$match": {
                    'dashboardId': dashboardId,
                    'userId': userId,
                    "device.type": "GATEWAYS"
                },
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "device.deviceUUID",
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
                    'typeId': 1,
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
                "$sort": {
                    "createdAt": -1
                }
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "device.deviceUUID",
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
                    'typeId': 1,
                    'attributeId': 1,
                    'device_info': 1
                }
            }
           
        ]
        cursors = self.collection.aggregate(pipeline)
        results = list(map(lambda r: self._cast_object_without_objectId(r), cursors))
        return results[0]
