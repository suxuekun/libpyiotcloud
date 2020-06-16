
from flask import Blueprint, request

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

# Import dashboards
from dashboards_app.modules.dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards_app.modules.dashboards.services.dashboard_service import DashboardService
from dashboards_app.modules.dashboards.dtos.dashboard_dto import DashboardDto

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

#  Import charts
from dashboards_app.modules.charts.services.gateway_attribute_service import GatewayAttributeService
from dashboards_app.modules.charts.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards_app.modules.charts.services.chart_type_service import ChartTypeService
from dashboards_app.modules.charts.repositories.chart_type_repository import ChartTypeRepository
from dashboards_app.modules.charts.repositories.chart_repository import ChartRepository
from dashboards_app.modules.charts.repositories.gateway_attribute_repository import GatewayAttributeRepository
from dashboards_app.modules.charts.services.chart_gateway_service import ChartGatewayService

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Repositories
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
chartTypeRepository = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="chartTypes")
attributeRepository = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")
chartRepository = ChartRepository(mongoclient=mongo_client, db = db, collectionName="charts")

# Init Dashboard Service
dashboardService = DashboardService(dashboardRepository)

# Init ChartTypeService
chartTypeService = ChartTypeService(chartTypeRepository)
chartTypeService.setup_chart_types()

# Init Dashboard Gateway Attributes services
gatewayAttributeService = GatewayAttributeService(attributeRepository)
gatewayAttributeService.setup_attributes()

# Init Gateway service 
chartGatewayService = ChartGatewayService(dashboardRepository, chartRepository, attributeRepository)

# Init routes
dashboards_blueprint = Blueprint('dashboards_blueprint', __name__)

# Dashboards
@dashboards_blueprint.route("", methods=['POST'])
@default_middleware
@login_required()
def create():
    body = request.get_json()
    user = request.environ.get('user')
    dto = DashboardDto(body)
    response = dashboardService.create(user["username"], dto)
    return response

@dashboards_blueprint.route("", methods=['GET'])
@default_middleware
@login_required()
def gets():
    user = request.environ.get('user')
    return dashboardService.gets(user["username"])

@dashboards_blueprint.route("/<id>", methods=['GET'])
@default_middleware
@login_required()
def get(id: str):
    return dashboardService.get(id)

@dashboards_blueprint.route("/<id>", methods=['PUT'])
@default_middleware
@login_required()
def update(id: str):
    body = request.get_json()
    dto = DashboardDto(body)
    response = dashboardService.updateNameAndOption(id, dto)
    return response

@dashboards_blueprint.route("/<id>", methods=['DELETE'])
def delete(id: str):
    response = dashboardService.delete(id)
    return response

#  Chart Types
@dashboards_blueprint.route("/charts/types/gateway", methods=['GET'])
def get_charrts_types_for_gateway():
    response = chartTypeService.gets_for_gateway()
    return response

@dashboards_blueprint.route("/charts/types/sensor", methods=['GET'])
def get_charts_tyoes_for_sensor():
    response = chartTypeService.gets_for_sensor()
    return response

#  Gateways attributes
@dashboards_blueprint.route("/gateways/attributes", methods=['GET'])
def get_attributes():
    response = gatewayAttributeService.gets()
    return response

#  Chart Gateways
@dashboards_blueprint.route("/<dashboardId>/gateways", methods=['POST'])
@default_middleware
@login_required()
def add_chart_gateway(dashboardId: str):
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = chartGatewayService.create(dashboardId, dto)
    return response

@dashboards_blueprint.route("/<dashboardId>/gateways/<id>", methods=['DELETE'])
@default_middleware
@login_required()
def delete_chart_gateway(dashboardId: str, id: str):
    response = chartGatewayService.delete(dashboardId, id)
    return response

@dashboards_blueprint.route("/<dashboardId>/gateways", methods=['GET'])
@default_middleware
@login_required()
def get_charts_gateway(dashboardId: str):
    response = chartGatewayService.gets(dashboardId=dashboardId)
    return response


@dashboards_blueprint.route("/<dashboardId>/gateways/<id>", methods=['GET'])
@default_middleware
@login_required()
def get_chart_gateway(dashboardId: str, id: str):
    response = chartGatewayService.get(dashboardId, id)
    return response