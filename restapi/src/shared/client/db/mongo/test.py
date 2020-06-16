from shared.client.connection.base import IotDBConnection
from shared.client.connection.test import TestMongoConnection
from shared.client.db.mongo.base import IotMongoDB


class TestMongoDB(IotDBConnection,IotMongoDB):
    def __init__(self):
        super(TestMongoDB,self).__init__()
        self._conn = TestMongoConnection().conn
        self._db = self.conn['iotcloud-database-test']

