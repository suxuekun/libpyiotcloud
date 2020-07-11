from pymongo import MongoClient

from rest_api_config import config
from shared.client.connection.base import IotDBConnection

class DefaultMongoConnection(IotDBConnection):
    def __init__(self):
        self._conn = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT) 