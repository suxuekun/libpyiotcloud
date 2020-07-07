
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from datetime import datetime, timezone

class ISensorRepository(BaseRepository, IMongoBaseRepository):

    def get_sensor_detail(self, id: str):
        pass

    def get_data_reading(self, ids: str, timestamp: int = None):
        pass


class SensorRepository(MongoBaseRepository, ISensorRepository):

    def get_data_reading(self, ids: str, timestamp: int = None):

        sensors = super().gets_with_ids(ids)
        sources = list(map(lambda s: s["source"], sensors))
        numbers = list(map(lambda s: s["number"], sensors))

        pipeline = [
            {
                '$match': {
                    'source': {
                        '$in': sources
                    },
                    'number': {
                        '$in': numbers
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'sensorreadings',
                    'localField': 'source',
                    'foreignField': 'source',
                    'as': 'readings'
                }
            },
            {
                '$lookup': {
                    'from': 'sensorreadingsdataset',
                    'localField': 'source',
                    'foreignField': 'source',
                    'as': 'dataset'
                }
            },
            {
                '$project': {
                    'source': 1,
                    'number': 1,
                    'enabled': 1,
                    'sensorname': 1,
                    'port': 1,
                    'name': 1,
                    'class': 1,
                    'readings': {
                        '$filter': {
                            'input': '$readings',
                            'as': 'reading',
                            'cond': {
                                '$and': [
                                    {
                                        '$eq': 
                                            [
                                                '$$reading.source',
                                                '$source'
                                            ]
                                    },
                                    {
                                        '$eq': [
                                            '$$reading.number',
                                            {
                                                '$toInt': '$number'
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                    'dataset': {
                        '$filter': {
                            'input': '$dataset',
                            'as': 'data',
                            'cond': {
                                '$and': [
                                    {
                                        '$eq': 
                                            [  
                                                '$$data.source',
                                                '$source'
                                            ]
                                    },
                                    {
                                        '$eq': [
                                            '$$data.number',
                                            {
                                                '$toInt': '$number'
                                            }
                                        ]
                                    },
                                    {'$gte': ['$$data.timestamp', timestamp]}
                                ]
                            }
                        }
                    }
                },
            },
        ]

        cursors = self.collection.aggregate(pipeline)

        items = list(cursors)
        for item in items:
            item["readings"] = list(
                map(lambda r: self._cast_object_without_objectId(r), item["readings"]))
            item["dataset"] = list(
                map(lambda r: self._cast_object_without_objectId(r), item["dataset"]))

        results = list(
            map(lambda r: self._cast_object_without_objectId(r), items))
        return results
