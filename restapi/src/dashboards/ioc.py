

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB, SensorMongoDb

from dashboards.repositories.chart_repository import ChartRepository
from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.repositories.device_repository import DeviceRepository

from dashboards.services.chart_gateway_service import ChartGatewayService
from dashboards.services.chart_sensor_service import ChartSensorService

from dashboards.services.dashboard_service import DashboardService
from dashboards.services.gateway_attribute_service import GatewayAttributeService

from dashboards.services.chart_type_service import ChartTypeService
from dashboards.repositories.chart_type_repository import ChartTypeRepository

from dashboards.repositories.sensor_repository import SensorRepository

#  Get config mongodb
mongoClient = DefaultMongoDB().conn
db = DefaultMongoDB().db

sensorMongoCLient = DefaultMongoConnection().conn
sensorDb = SensorMongoDb().db

dashboardRepository = DashboardRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards")
attributeRepository = GatewayAttributeRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_gatewayAttributes")
chartRepository = ChartRepository(
    mongoclient=mongoClient, db=db, collectionName="dashboards_charts")

chartTypeRepository = ChartTypeRepository(mongoclient=mongoClient, db = db, collectionName="dashboards_chartTypes")


deviceRepository = DeviceRepository(
    mongoclient=mongoClient, db=db, collectionName="devices")

sensorRepository = SensorRepository(mongoclient=sensorMongoCLient, db = sensorDb, collectionName="i2csensors")


dashboardService =  DashboardService(dashboardRepository)
chartGatewayService = ChartGatewayService(dashboardRepository, chartRepository, attributeRepository, deviceRepository, dashboardService)

def init_chart_gateway_service():
    return chartGatewayService
    
def init_chart_sensor_service():
    return ChartSensorService(
        dashboardRepository, chartRepository, attributeRepository, deviceRepository, sensorRepository, dashboardService)

def init_dashboard_service():
    return dashboardService

def init_gateway_attribute_service():
    return GatewayAttributeService(attributeRepository)

def init_chart_type_service():
    return ChartTypeService(chartTypeRepository)

def init_sensor_repository():
    return sensorRepository;
