
from flask import Blueprint, request


from dashboards_app.repositories.dashboard_repository import DashboardRepository
from dashboards_app.services.dashboard_service import DashboardService
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.dtos.chart_gateway_dto import ChartGatewayDto
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB
from shared.middlewares.request.permission.login import login_required
from dashboards_app.services.chart_type_service import ChartTypeService
from dashboards_app.services.gateway_attribute_service import GatewayAttributeService
from dashboards_app.repositories.chart_type_repository import ChartTypeRepository
from dashboards_app.repositories.gateway_attribute_repository import GatewayAttributeRepository
from dashboards_app.services.gateway_service import GatewayService


#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Dashboard Service
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
dashboardService = DashboardService(dashboardRepository)

# Init ChartTypeService
chartTypeRepo = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="chartTypes")
chartTypeService = ChartTypeService(chartTypeRepo)
chartTypeService.setup_chart_types()

# Init Dashboard Gateway Attributes services
attributeRepo = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")
gatewayAttributeService = GatewayAttributeService(attributeRepo)
gatewayAttributeService.setup_attributes()

# Init Gateway service 
gatewayService = GatewayService(dashboardRepository)

# Init routes
dashboards_blueprint = Blueprint('dashboards_blueprint', __name__)

# Dashboards
@dashboards_blueprint.route("", methods=['POST'])
@login_required()
def create():
    body = request.get_json()
    user = request.environ.get('user')
    dto = DashboardDto(body)
    response = dashboardService.create(user["username"], dto)
    return response

@dashboards_blueprint.route("", methods=['GET'])
@login_required()
def gets():
    user = request.environ.get('user')
    print(user)
    return dashboardService.gets(user["username"])

@dashboards_blueprint.route("/<id>", methods=['GET'])
@login_required()
def get(id: str):
    return dashboardService.get(id)

@dashboards_blueprint.route("/<id>", methods=['PUT'])
@login_required()
def update(id: str):
    body = request.get_json()
    dto = DashboardDto(body)
    response = dashboardService.updateNameAndOption(id, dto)
    return response

@dashboards_blueprint.route("/<id>", methods=['DELETE'])
@login_required()
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
def add_chart_gateway(dashboardId: str):
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = gatewayService.add(dashboardId, dto)
    return response

@dashboards_blueprint.route("/<dashboardId>/gateways/<id>", methods=['DELETE'])
def delete_chart_gateway(dashboardId: str, id: str):
    response = gatewayService.delete(dashboardId, id)
    return response

