from shared.client.connection.base import IotDBConnection
from shared.client.connection.test import TestMongoConnection
from shared.client.db.mongo.base import IotMongoDB


class TestMongoDB(IotDBConnection,IotMongoDB):
    def __init__(self):
        super(TestMongoDB,self).__init__()
        self._conn = TestMongoConnection().conn
        self._db = self.conn['iotcloud-database-test']


if __name__ == '__main__':
    db = TestMongoDB()
    client = db.conn
    orders = client.db.orders
    inventory = client.db.inventory
    with client.start_session() as session:
        with session.start_transaction():
            orders.insert_one({"sku": "abc123", "qty": 100}, session=session)
            inventory.update_one({"sku": "abc123", "qty": {"$gte": 100}},
                                 {"$inc": {"qty": -100}}, session=session)

            item = orders.find_one({"sku": "abc123"})
            print(item)
            raise Exception('wtf')

    item = orders.find_one({"sku": "abc123"})
    print(item)


