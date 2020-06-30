

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

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

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

dashboardRepository = DashboardRepository(
    mongoclient=mongo_client, db=db, collectionName="dashboards")
attributeRepository = GatewayAttributeRepository(
    mongoclient=mongo_client, db=db, collectionName="dashboards_gatewayAttributes")
chartRepository = ChartRepository(
    mongoclient=mongo_client, db=db, collectionName="dashboards_charts")

chartTypeRepository = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="dashboards_chartTypes")

deviceRepository = DeviceRepository(
    mongoclient=mongo_client, db=db, collectionName="devices")

def init_chart_gateway_service():
    return ChartGatewayService(
        dashboardRepository, chartRepository, attributeRepository, deviceRepository)
    
def init_chart_sensor_service():
    return ChartSensorService(
        dashboardRepository, chartRepository, attributeRepository, deviceRepository)

def init_dashboard_service():
    return DashboardService(dashboardRepository)

def init_gateway_attribute_service():
    return GatewayAttributeService(attributeRepository)

def init_chart_type_service():
    return ChartTypeService(chartTypeRepository)