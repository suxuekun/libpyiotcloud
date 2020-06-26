from rest_api_config import config
from shared.client.connection.base import IotDBConnection
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.base import IotMongoDB
from pymongo import MongoClient


class DefaultMongoDB(IotDBConnection,IotMongoDB):
    def __init__(self):
        super(DefaultMongoDB,self).__init__()
        self._conn = DefaultMongoConnection().conn
        self._db = self.conn[config.CONFIG_MONGODB_DB]


class SensorMongoDb(IotDBConnection, IotMongoDB):
    def __init__(self, connectionString: str):
        super(SensorMongoDb,self).__init__()
        self._conn = MongoClient(connectionString)
        self._db = self.conn[config.CONFIG_MONGODB_DB]

