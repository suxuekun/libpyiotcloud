from pymongo import MongoClient
from shared.client.connection.base import IotDBConnection

class TestMongoConnection(IotDBConnection):
    def __init__(self):
        self._conn = MongoClient('localhost',27017)