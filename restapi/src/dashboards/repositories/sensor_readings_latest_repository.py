
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.exceptions import QueriedManyException


class ISensorReadingsLatestRepository(IMongoBaseRepository):
    def gets_dataset_with_same_gateway(self, sensors, timestampBegin, timestampEnd):
        pass

    def gets_dataset(self, sensors, timestampBegin, timestampEnd):
        pass


class SensorReadingsLatestRepository(MongoBaseRepository, ISensorReadingsLatestRepository):

    def gets_dataset(self, sensors, timestampBegin, timestampEnd):
        if len(sensors) == 0:
            raise QueriedManyException("Cannot query sensors")

        setsSensorsDeviceid = set()
        for sensor in sensors:
            if sensor["deviceid"] not in setsSensorsDeviceid:
                setsSensorsDeviceid.add(sensor["deviceid"])

        totalReports = []
        for gatewayUUID in setsSensorsDeviceid:
            filterSensors = list(
                filter(lambda s: s["deviceid"] == gatewayUUID, sensors))
            reports = self.gets_dataset_with_same_gateway(
                gatewayUUID, filterSensors, timestampBegin, timestampEnd)
            totalReports.extend(reports)

        return totalReports

    def gets_dataset_with_same_gateway(self, gatewayUUID, sensors, timestampBegin, timestampEnd):

        sources = list(map(lambda s: s["source"], sensors))
        numbers = list(map(lambda s: int(s["number"]), sensors))
        collectionName = "sensors_readings_dataset_" + gatewayUUID
        pipeline = [
            {
                '$match': {
                    'source': {
                        '$in': sources
                    },
                    'number': {
                        '$in': numbers
                    },
                }
            },
            {
                '$lookup': {
                    'from': collectionName,
                    'let': {
                        'sensors_readings_latest_source': '$source',
                        'sensors_readings_latest_number': '$number',
                    },
                    'pipeline': [
                        {
                            '$match':
                                {
                                    '$expr': {
                                        '$and': [
                                            {
                                                '$eq': [
                                                    '$number',
                                                    '$$sensors_readings_latest_number'
                                                ]
                                            },
                                            {'$gte': ['$timestamp',
                                                      timestampBegin]},
                                            {'$lte': [
                                                '$timestamp', timestampEnd]}
                                        ]
                                    }
                                }
                        }
                    ],
                    'as': 'dataset'
                }
            },
            {
                '$project': {
                    'source': 1,
                    'number': 1,
                    'sensor_readings': 1,
                    'dataset': 1
                },
            },
        ]

        cursors = self.collection.aggregate(pipeline)
        sensorsReports = list(cursors)
        reports = []

        for s in sensors:
            newReport = {}
            newReport["sensorId"] = str(s["_id"])
            newReport["sensorname"] = s["sensorname"]
            newReport["port"] = s["port"]
            newReport["name"] = s["name"]
            newReport["class"] = s["class"]
            newReport["source"] = s["source"]
            newReport["number"] = int(s["number"])
            newReport["gatewayUUID"] = s["deviceid"]
            newReport["unit"] = s["unit"]
            newReport["format"] = s["format"]
            newReport["accuracy"] = s["accuracy"]
            newReport["minmax"] = s["minmax"]
            newReport["enabled"] = s["enabled"]

            sensorReport = self._get_sensor_report_detail(
                s["source"], int(s["number"]), sensorsReports)

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
