
from shared.core.base_repository import BaseRepository
from shared.core.mongo_base_repository import MongoBaseRepository, IMongoBaseRepository
from shared.core.exceptions import QueriedManyException
from shared.client.db.mongo.default import SensorDataMongoDb

USE_OPTIMIZED_QUERY = False


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
            filterSensors = list(filter(lambda s: s["deviceid"] == gatewayUUID, sensors))

            if USE_OPTIMIZED_QUERY:
                # using find() with combo indexing on 'sid' and 'timestamp' - faster by 300-1000 times for 1GB above
                reports = self.gets_dataset_with_same_gateway_ex(gatewayUUID, filterSensors, timestampBegin, timestampEnd)
            else:
                # using aggregate() with indexing on 'sid'
                reports = self.gets_dataset_with_same_gateway(gatewayUUID, filterSensors, timestampBegin, timestampEnd)

            totalReports.extend(reports)
        
        return totalReports

    def gets_dataset_with_same_gateway(self, gatewayUUID, sensors, timestampBegin, timestampEnd):

        sids = list(map(lambda s: "{}.{}".format(s["source"], s["number"]), sensors))
        collectionName = "sensors_readings_dataset_" + gatewayUUID
        pipeline = [
            {
                '$match': {
                    'sid': {
                        '$in': sids
                    },
                }
            },
            {
                '$lookup': {
                    'from': collectionName,
                    'let': {
                        'sensors_readings_latest_sid': '$sid',
                    },
                    'pipeline': [
                        {
                            '$match':
                                {
                                    '$expr': {
                                        '$and': [
                                            {'$eq': ['$sid', '$$sensors_readings_latest_sid'] },
                                            {'$gte': ['$timestamp', timestampBegin]},
                                            {'$lte': ['$timestamp', timestampEnd]}
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
                    'sid': 1,
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
            newReport["gatewayName"] = s["gateway"]["devicename"]
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

    def gets_dataset_with_same_gateway_ex(self, gatewayUUID, sensors, timestampBegin, timestampEnd):

        collectionName = "sensors_readings_dataset_" + gatewayUUID
        client_sensor = SensorDataMongoDb().conn["iotcloud-sensordata-database"]
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
            newReport["gatewayName"] = s["gateway"]["devicename"]
            newReport["unit"] = s["unit"]
            newReport["format"] = s["format"]
            newReport["accuracy"] = s["accuracy"]
            newReport["minmax"] = s["minmax"]
            newReport["enabled"] = s["enabled"]

            sid = "{}.{}".format(s["source"], s["number"])
            newReport["dataset"] = list(client_sensor[collectionName].find(
                { 'sid': sid, 'timestamp': { '$gte': timestampBegin, '$lte': timestampEnd } },
                { '_id': 0, 'sid': 0 }
            ))
            if len(newReport["dataset"]):
                sensor_readings = list(client_sensor["sensors_readings_latest"].find(
                    { 'deviceid': s["deviceid"], 'sid': sid },
                    { '_id': 0, 'sensor_readings': 1 }
                ))
                newReport["sensor_readings"] = sensor_readings[0]["sensor_readings"]
            else:
                newReport["sensor_readings"] = None
            reports.append(newReport)
        return reports

    def _get_sensor_report_detail(self, source: str, number: int, reports):
        sid = "{}.{}".format(source, number)
        for r in reports:
            if r["sid"] == sid:
                return r

        return None

    def _get_sensor_detail(self, source: str, number: int, sensors):

        for sensor in sensors:
            if sensor["source"] == source and sensor["number"] == str(number):
                return sensor
        return None
