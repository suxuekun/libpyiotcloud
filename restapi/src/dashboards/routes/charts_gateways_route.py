
from flask import Blueprint, request

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

#  Import charts
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from dashboards.repositories.chart_repository import ChartRepository
from dashboards.repositories.gateway_attribute_repository import GatewayAttributeRepository

from dashboards.services.chart_gateway_service import ChartGatewayService
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.repositories.device_repository import DeviceRepository

from flask import Blueprint, request

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Repositories
dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
attributeRepository = GatewayAttributeRepository(mongoclient=mongo_client, db = db, collectionName="gatewayAttributes")
chartRepository = ChartRepository(mongoclient=mongo_client, db = db, collectionName="charts")
deviceRepository = DeviceRepository(mongoclient=mongo_client, db = db, collectionName="devices")

# Init Gateway service 
chartGatewayService = ChartGatewayService(dashboardRepository, chartRepository, attributeRepository, deviceRepository)

# Init routes
charts_gateways_blueprint = Blueprint('charts_gateways_blueprint', __name__)


# ------- Chart Gateways ------
@charts_gateways_blueprint.route("/", methods=['POST'])
@default_middleware
@login_required()
def add_chart_gateway(dashboardId: str):
    print("Chan wa")
    print(dashboardId)
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = chartGatewayService.create_for_gateway(dashboardId, dto)
    return response

@charts_gateways_blueprint.route("/<id>", methods=['DELETE'])
@default_middleware
@login_required()
def delete_chart_gateway(dashboardId: str, id: str):
    response = chartGatewayService.delete(dashboardId, id)
    return response

@charts_gateways_blueprint.route("/", methods=['GET'])
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


@charts_gateways_blueprint.route("/<id>", methods=['GET'])
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