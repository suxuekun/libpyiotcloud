
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from datetime import datetime, timezone
from bson.objectid import ObjectId


class ISensorRepository(BaseRepository, IMongoBaseRepository):
    def get_by_source_and_number(self, source: str, number: str):
        pass

    def gets_sensors(self, ids):
        pass


class SensorRepository(MongoBaseRepository, ISensorRepository):

    def get_by_source_and_number(self, source, number):
        query = {
            "source": source,
            "number": number
        }

        return super().get_one(query)

    def gets_sensors(self, ids):
        objectIds = list(map(lambda id:  ObjectId(id), ids))
        pipeline = [
            {
                "$match": {
                    '_id': {
                        '$in': objectIds
                    }
                }
            },
            {
                "$lookup": {
                    'from': 'devices',
                    'localField': 'deviceid',
                    'foreignField': 'deviceid',
                    'as': 'gateway'
                }
            },
            {
                "$unwind": {
                    'path': '$gateway',
                    "preserveNullAndEmptyArrays": True
                }
            },
        ]

        cursors = self.collection.aggregate(pipeline)
        sensorsReports = list(cursors)

        return sensorsReports
