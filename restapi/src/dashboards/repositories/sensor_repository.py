
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from datetime import datetime, timezone


class ISensorRepository(BaseRepository, IMongoBaseRepository):

    def get_sensor_detail(self, id: str):
        pass

    def get_data_reading(self, id: str, timestamp: int = None):
        pass


class SensorRepository(MongoBaseRepository, ISensorRepository):

    def get_data_reading(self, id: str, timestamp: int = None):
        sensor = super().getById(id)
        print("SOurce: ")
        print(sensor["source"])
        print("Number")
        print(sensor["number"])
        print("Timestamp: ")
        print(timestamp)
        print("Convert TimeStamp: ")
        print(datetime.fromtimestamp(timestamp))
        pipeline = [
            {
                '$match': {
                    'source': sensor["source"],
                    'number': sensor["number"],
                }
            },
            {
                '$lookup': {
                    'from': 'sensorreadingsdataset',
                    'localField': 'source',
                    'foreignField': 'source',
                    'as': 'readings'
                }
            },
            {
                '$project': {
                    'source': 1,
                    'number': 1,
                    'readings': {
                        '$filter': {
                            'input': '$readings',
                            'as': 'reading',
                            'cond': {
                                '$and': [
                                    {'$eq': ['$$reading.source',
                                             sensor['source']]},
                                    {'$eq': ['$$reading.number',
                                             int(sensor['number'])]},
                                    {'$gte': ['$$reading.timestamp', timestamp]}
                                ]
                            }
                        }
                    }
                }
            }
        ]

        cursors = self.collection.aggregate(pipeline)

        items = list(cursors)
        for item in items:
            item["readings"] = list(
                map(lambda r: self._cast_object_without_objectId(r), item["readings"]))
            for read in item["readings"]:
                read["timestamp"] = datetime.fromtimestamp(read["timestamp"])

        results = list(
            map(lambda r: self._cast_object_without_objectId(r), items))
        return results
