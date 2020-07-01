from rest_api_config import config
from shared.client.connection.base import IotDBConnection
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.base import IotMongoDB
from pymongo import MongoClient




class DefaultMongoDB(IotDBConnection, IotMongoDB):
    def __init__(self):
        super(DefaultMongoDB, self).__init__()
        self._conn = DefaultMongoConnection().conn
        self._db = self.conn[config.CONFIG_MONGODB_DB]

SENSOR_CONNECTION = "mongodb+srv://" + config.CONFIG_MONGODB_USERNAME + ":" + config.CONFIG_MONGODB_PASSWORD + "@" + config.CONFIG_MONGODB_HOST2 + "/" + config.CONFIG_MONGODB_DB + "?retryWrites=true&w=majority"

class SensorMongoDb(IotDBConnection, IotMongoDB):
    def __init__(self):
        super(SensorMongoDb, self).__init__()
        if "mongodb.net" in config.CONFIG_MONGODB_HOST2:
            self._conn = MongoClient(SENSOR_CONNECTION)
            self._db = self.conn[config.CONFIG_MONGODB_DB]
        else:
            self._conn = DefaultMongoConnection().conn
            self._db = self.conn[config.CONFIG_MONGODB_DB]

