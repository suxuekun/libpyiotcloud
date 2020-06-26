
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository


class ISensorRepository(BaseRepository, IMongoBaseRepository):

    def get_sensor_detail(self, id: str):
        pass

    def get_data_reading(self, id: str, timestamp: str = None):
        pass


class SensorRepository(MongoBaseRepository, ISensorRepository):

    def get_data_reading(self, id: str, timestamp: str = None):

        sensor = super().getById(id)
        print("Cho ma" + sensor["source"] + " -- " + sensor["number"])
        pipeline = [
            {
                '$match': {
                    'source': sensor["source"],
                    'number': sensor["number"]
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
                                    {'$eq': ['$$reading.source', sensor['source']]},
                                    {'$eq': ['$$reading.number', int(sensor['number'])] }
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

        results = list(
            map(lambda r: self._cast_object_without_objectId(r), items))
        return results
