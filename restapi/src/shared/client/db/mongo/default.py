from rest_api_config import config
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.base import IotMongoDB


class DefaultMongoDB(DefaultMongoConnection,IotMongoDB):
    def __init__(self):
        super(DefaultMongoDB,self).__init__()
        self._db = self.conn[config.CONFIG_MONGODB_DB]

