
from flask import Blueprint, request

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

from dashboards.ioc import init_chart_gateway_service
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto

# Init Gateway service 
chartGatewayService = init_chart_gateway_service()

# Init routes
charts_gateway_blueprint = Blueprint('charts_gateway_blueprint', __name__)

# ------- Chart Gateways ------
@charts_gateway_blueprint.route("", methods=['POST'])
@default_middleware
@login_required()
def create(dashboardId: str):
    print("Try to create chart")
    body = request.get_json()
    dto = ChartGatewayDto(body)
    response = chartGatewayService.create(dashboardId, dto)
    return response

@charts_gateway_blueprint.route("/<chartId>", methods=['DELETE'])
@default_middleware
@login_required()
def delete(dashboardId: str, chartId: str):
    response = chartGatewayService.delete(dashboardId, chartId)
    return response

@charts_gateway_blueprint.route("", methods=['GET'])
@default_middleware
@login_required()
def gets(dashboardId: str):
    user = request.environ.get('user')
    queryParams = request.args
    query = {
        "attributeId": queryParams.get("attributeId", ""),
        "filterId": queryParams.get("filterId", "")
    }
    response = chartGatewayService.gets(dashboardId, user["username"], query)
    return response

@charts_gateway_blueprint.route("/<chartId>", methods=['GET'])
@default_middleware
@login_required()
def get(dashboardId: str, chartId: str):
    user = request.environ.get('user')
    queryParams = request.args
    query = {
        "attributeId": queryParams.get("attributeId", ""),
        "filterId": queryParams.get("filterId", "")
    }
    response = chartGatewayService.get(dashboardId, user["username"], chartId, query)
    return response
