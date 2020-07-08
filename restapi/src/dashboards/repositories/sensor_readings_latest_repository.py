
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
                                    {'$gte': ['$$data.timestamp',
                                              timestampBegin]},
                                    {'$lte': ['$$data.timestamp', timestampEnd]},
                                ]
                            }
                        }
                    }
                },
            },
        ]
        cursors = self.collection.aggregate(pipeline)
        sensorsReports = list(cursors)

        reports = []
        for s in sensors:
            newReport = {}
            newReport["sensorId"] = str(s["_id"])
            newReport["enabled"] = s["enabled"]
            newReport["sensorname"] = s["sensorname"]
            newReport["port"] = s["port"]
            newReport["name"] = s["name"]
            newReport["class"] = s["class"]
            newReport["source"] = s["source"]
            newReport["number"] = int(s["number"])
           
            sensorReport = self._get_sensor_report_detail(
                s["source"], int(s["number"]), sensorsReports)

            print(sensorReport)
            if sensorReport is not None:
                newReport["dataset"] = list(
                    map(lambda r: self._cast_object_without_objectId(r), sensorReport["dataset"]))
                newReport["sensor_readings"] = sensorReport["sensor_readings"]
            else:
                newReport["dataset"] = []
                newReport["sensor_readings"] = None
            
            reports.append(newReport)

        return reports

    def _get_sensor_report_detail(self, source: str, number: int, reports):
        for r in reports:
            if r["source"] == source and r["number"] == number:
                return r

        return None

    def _get_sensor_detail(self, source: str, number: int, sensors):

        for sensor in sensors:
            if sensor["source"] == source and sensor["number"] == str(number):
                return sensor
        return None
