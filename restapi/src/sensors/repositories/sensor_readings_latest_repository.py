
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.exceptions import QueriedManyException


class ISensorReadingsLatestRepository(IMongoBaseRepository):
    def gets_dataset_with_same_gateway(self, sensors, timestamp):
        pass


class SensorReadingsLatestRepository(MongoBaseRepository, ISensorReadingsLatestRepository):

    def gets_dataset_with_same_gateway(self, sensors, timestampBegin, timestampEnd):

        if len(sensors) == 0:
            raise QueriedManyException("Cannot query sensors")

        gatewayUUID = sensors[0]["deviceid"]
        for sensor in sensors:
            if sensor["deviceid"] != gatewayUUID:
                raise QueriedManyException("Sensors is not the same gateway")

        sources = list(map(lambda s: s["source"], sensors))
        numbers = list(map(lambda s: int(s["number"]), sensors))

        gatewayUUID = sensors[0]["deviceid"]
        for sensor in sensors:
            if sensor["deviceid"] != gatewayUUID:
                raise QueriedManyException("Sensors is not the same gateway")

        collectionName = "sensors_readings_dataset_" + gatewayUUID
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
                    'from': collectionName,
                    'localField': 'source',
                    'foreignField': 'source',
                    'as': 'dataset'
                }
            },
            {
                '$project': {
                    'source': 1,
                    'number': 1,
                    'sensor_readings': 1,
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
                                        '$eq':
                                            [
                                                '$$data.number',
                                                '$number'
                                            ]
                                    },
                                    {'$gte': ['$$data.timestamp', timestampBegin]},
                                    {'$lte': ['$$data.timestamp', timestampEnd]},
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
            item["dataset"] = list(
                map(lambda r: self._cast_object_without_objectId(r), item["dataset"]))
            item["readings"] = item["sensor_readings"]
            sensor = self._get_sensor_detail(item["source"], item["number"], sensors)
            if sensor is not None:
                
                # Replace Id by sensor Id
                item["sensorId"] = str(sensor["_id"])
                item["enabled"] = sensor["enabled"]
                item["sensorname"] = sensor["sensorname"]
                item["port"] = sensor["port"]
                item["name"] = sensor["name"]
                item["class"] = sensor["class"]
            
        return items


    def _get_sensor_detail(self, source: str, number: int, sensors):

        for sensor in sensors:
            if sensor["source"] == source and sensor["number"] == str(number):
                return sensor
        return None
