

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB, SensorDataMongoDb
from shared.client.clients.database_client import db_client

from dashboards.repositories.chart_gateway_repository import ChartGatewayRepository
from dashboards.repositories.chart_sensor_repository import ChartSensorRepository

from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.repositories.device_repository import DeviceRepository

from dashboards.services.chart_gateway_service import ChartGatewayService
from dashboards.services.chart_sensor_service import ChartSensorService

from dashboards.services.dashboard_service import DashboardService
from dashboards.services.gateway_attribute_service import GatewayAttributeService

from dashboards.services.chart_type_service import ChartTypeService
from dashboards.repositories.chart_type_repository import ChartTypeRepository

from dashboards.repositories.sensor_readings_latest_repository import SensorReadingsLatestRepository, ISensorReadingsLatestRepository
from dashboards.repositories.sensor_repository import SensorRepository

from dashboards.repositories.heart_beat_repository import HeartBeatRepository
from dashboards.repositories.menos_alert_repository import MenosAlertRepository
from dashboards.repositories.storage_usage_repository import StorageUsageRepository

#  Get config mongodb
mongoClient = DefaultMongoDB().conn
db = DefaultMongoDB().db

sensorDataMongoClient = SensorDataMongoDb().conn
sensorDataDb = SensorDataMongoDb().db

dashboardRepository = DashboardRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards")
attributeRepository = GatewayAttributeRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_gatewayAttributes")

chartGatewayRepository = ChartGatewayRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_charts_gateways")

chartSensorRepository = ChartSensorRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_charts_sensors")

chartTypeRepository = ChartTypeRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_chartTypes")

deviceRepository = DeviceRepository(
    mongoclient=mongoClient, db=db, collectionName="devices")

sensorRepository = SensorRepository(
    mongoclient=mongoClient, db=db, collectionName="sensors")
    
sensorReadingsLatestRepository = SensorReadingsLatestRepository(
    mongoclient=sensorDataMongoClient, db=sensorDataDb, collectionName="sensors_readings_latest")


heartBeatRepository = HeartBeatRepository(db_client)
menoAlertRepository = MenosAlertRepository(db_client)
storageUsageRepository = StorageUsageRepository(db_client)

dashboardService = DashboardService(dashboardRepository, chartGatewayRepository, chartSensorRepository)

chartGatewayService = ChartGatewayService(
    dashboardRepository, chartGatewayRepository, attributeRepository, deviceRepository, heartBeatRepository, menoAlertRepository, storageUsageRepository, dashboardService)

chartSensorService = ChartSensorService(
    dashboardRepository, chartSensorRepository, attributeRepository, deviceRepository, sensorRepository, sensorReadingsLatestRepository, dashboardService)

def init_chart_gateway_service():
    return chartGatewayService


def init_chart_sensor_service():
    return chartSensorService


def init_dashboard_service():
    return dashboardService


def init_gateway_attribute_service():
    return GatewayAttributeService(attributeRepository)


def init_chart_type_service():
    return ChartTypeService(chartTypeRepository)


def init_sensor_repository():
    return sensorRepository


def get_sensor_repository():
    return sensorRepository
