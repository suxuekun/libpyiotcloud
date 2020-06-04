from pymongo import MongoClient

from rest_api_config import config
from shared.client.connection.base import IotDBConnection
from shared.utils.singleton_util import Singleton


class DefaultMongoConnection(IotDBConnection,metaclass=Singleton):
    def __init__(self):
        self._conn = MongoClient(config.CONFIG_MONGODB_HOST, config.CONFIG_MONGODB_PORT)




