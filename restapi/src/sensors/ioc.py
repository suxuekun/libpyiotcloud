


from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB, SensorDataMongoDb
from sensors.repositories.sensor_readings_latest_repository import SensorReadingsLatestRepository, ISensorReadingsLatestRepository
from sensors.repositories.sensor_repository import SensorRepository

defaultMongoClient = DefaultMongoDB().conn
db = DefaultMongoDB().db

sensorDataMongoClient = SensorDataMongoDb().conn
sensorDataDb = SensorDataMongoDb().db


sensorRepository = SensorRepository(mongoclient=defaultMongoClient, db = db, collectionName="sensors")
def get_sensor_repository():
    return sensorRepository


sensorReadingsLatestRepository = SensorReadingsLatestRepository(mongoclient=sensorDataMongoClient, db = sensorDataDb, collectionName="sensors_readings_latest")
def get_sensor_readings_latest_repository() -> ISensorReadingsLatestRepository: 
    return sensorReadingsLatestRepository






