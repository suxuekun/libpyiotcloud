
from flask import Blueprint, request

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

#  Import charts
from charts.services.gateway_attribute_service import GatewayAttributeService
from charts.dtos.chart_gateway_dto import ChartGatewayDto
from charts.services.chart_type_service import ChartTypeService
from charts.repositories.chart_type_repository import ChartTypeRepository
from charts.repositories.chart_repository import ChartRepository
from charts.repositories.gateway_attribute_repository import GatewayAttributeRepository
from charts.services.chart_gateway_service import ChartGatewayService
from dashboards.repositories.dashboard_repository import DashboardRepository

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Repositories
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
chartTypeRepository = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="chartTypes")
attributeRepository = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")
chartRepository = ChartRepository(mongoclient=mongo_client, db = db, collectionName="charts")

# Init ChartTypeService
chartTypeService = ChartTypeService(chartTypeRepository)
chartTypeService.setup_chart_types()

# Init Dashboard Gateway Attributes services
gatewayAttributeService = GatewayAttributeService(attributeRepository)
gatewayAttributeService.setup_attributes()

# Init Gateway service 
chartGatewayService = ChartGatewayService(dashboardRepository, chartRepository, attributeRepository)

# Init routes
charts_blueprint = Blueprint('charts_blueprint', __name__)


#  Chart Types
@charts_blueprint.route("/types/gateway", methods=['GET'])
def get_charrts_types_for_gateway():
    response = chartTypeService.gets_for_gateway()
    return response

@charts_blueprint.route("/types/sensor", methods=['GET'])
def get_charts_tyoes_for_sensor():
    response = chartTypeService.gets_for_sensor()
    return response

#  Gateways attributes
@charts_blueprint.route("/gateways/attributes", methods=['GET'])
def get_attributes():
    response = gatewayAttributeService.gets()
    return response

#  Chart Gateways
@charts_blueprint.route("/<dashboardId>/gateways", methods=['POST'])
@default_middleware
@login_required()
def add_chart_gateway(dashboardId: str):
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = chartGatewayService.create(dashboardId, dto)
    return response

@charts_blueprint.route("/<dashboardId>/gateways/<id>", methods=['DELETE'])
@default_middleware
@login_required()
def delete_chart_gateway(dashboardId: str, id: str):
    response = chartGatewayService.delete(dashboardId, id)
    return response

@charts_blueprint.route("/<dashboardId>/gateways", methods=['GET'])
@default_middleware
@login_required()
def get_charts_gateway(dashboardId: str):
    response = chartGatewayService.gets(dashboardId=dashboardId)
    return response


@charts_blueprint.route("/<dashboardId>/gateways/<id>", methods=['GET'])
@default_middleware
@login_required()
def get_chart_gateway(dashboardId: str, id: str):
    response = chartGatewayService.get(dashboardId, id)
    return response