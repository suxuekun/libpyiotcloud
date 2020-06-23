
from flask import Blueprint, request

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

# Import dashboards
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.services.dashboard_service import DashboardService
from dashboards.dtos.dashboard_dto import DashboardDto

#  Import charts
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.repositories.chart_repository import ChartRepository
from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository

from dashboards.services.chart_gateway_service import ChartGatewayService
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.repositories.device_repository import DeviceRepository

# Import gateway attribute
from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required


#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Repositories
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")

# Init Dashboard Service
dashboardService = DashboardService(dashboardRepository)

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

# ------- Chart Gateways ------

# Init Repositories
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
attributeRepository = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")
chartRepository = ChartRepository(mongoclient=mongo_client, db = db, collectionName="charts")
deviceRepository = DeviceRepository(mongoclient=mongo_client, db = db, collectionName="devices")

# Init Gateway service 
chartGatewayService = ChartGatewayService(dashboardRepository, chartRepository, attributeRepository, deviceRepository)

@dashboards_blueprint.route("/<dashboardId>/gateways", methods=['POST'])
@default_middleware
@login_required()
def add_chart_gateway(dashboardId: str):
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = chartGatewayService.create_for_gateway(dashboardId, dto)
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
    user = request.environ.get('user')
    queryParams = request.args
    query = {
        "attributeId": queryParams.get("attributeId", ""),
        "filterId": queryParams.get("filterId", "")
    }
    print(query)
    response = chartGatewayService.gets(dashboardId, user["username"], query)
    return response


@dashboards_blueprint.route("/<dashboardId>/gateways/<id>", methods=['GET'])
@default_middleware
@login_required()
def get_chart_gateway(dashboardId: str, id: str):
    
    queryParams = request.args
    query = {
        "attributeId": queryParams.get("attributeId", ""),
        "filterId": queryParams.get("filterId", "")
    }
    response = chartGatewayService.get(dashboardId, id, query)
    return response