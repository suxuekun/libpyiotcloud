

from flask import Blueprint, request
from dashboards.dtos.chart_sensor_dto import ChartSensorDto
from dashboards.dtos.chart_sensor_query import ChartSensorQuery, ChartComparisonQuery
from dashboards.ioc import init_chart_sensor_service
from datetime import datetime

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required
chartSensorService = init_chart_sensor_service()

# Init routes
charts_sensor_blueprint = Blueprint('charts_sensor_blueprint', __name__)

@charts_sensor_blueprint.route("", methods=['POST'])
@default_middleware
@login_required()
def create(dashboardId: str):
    body = request.get_json()
    dto = ChartSensorDto(body)
    response = chartSensorService.create(dashboardId, dto)
    return response

@charts_sensor_blueprint.route("", methods=['GET'])
@default_middleware
@login_required()
def gets(dashboardId: str):
    user = request.environ.get('user')
    queryParams = request.args
    query = ChartSensorQuery()
    query.points = int(queryParams.get("points", 30))
    query.minutes = int(queryParams.get("minutes", 5))
    query.timestamp = int(queryParams.get("timestamp", int(datetime.now().timestamp())))
    response = chartSensorService.gets(dashboardId, user["username"], query)
    return response

@charts_sensor_blueprint.route("/<chartId>", methods=['GET'])
@default_middleware
@login_required()
def get(dashboardId: str, chartId: str):
    user = request.environ.get('user')
    queryParams = request.args
    query = ChartSensorQuery()
    query.points = int(queryParams.get("points", 30))
    query.minutes = int(queryParams.get("minutes", 5))
    query.timestamp = int(queryParams.get("timestamp", int(datetime.now().timestamp())))
    response = chartSensorService.get(dashboardId, user["username"], chartId, query)
    return response

@charts_sensor_blueprint.route("/<chartId>", methods=['DELETE'])
@default_middleware
@login_required()
def delete(dashboardId: str, chartId: str):
    response = chartSensorService.delete(dashboardId, chartId)
    return response

@charts_sensor_blueprint.route("/comparison", methods=['GET'])
@default_middleware
@login_required()
def gets_compare(dashboardId: str):
    user = request.environ.get('user')
    queryParams = request.args

    query = ChartComparisonQuery()
    query.points = int(queryParams.get("points", 30))
    query.minutes = int(queryParams.get("minutes", 5))
    query.timestamp = int(queryParams.get("timestamp", int(datetime.now().timestamp())))
    query.chartsId = list(queryParams.getlist("chartsId"))

    response = chartSensorService.compare(dashboardId, user["username"], query)
    return response

@charts_sensor_blueprint.route("/data/readings/<sensorId>", methods=['GET'])
@default_middleware
def get_test(dashboardId: str, sensorId: str):
    response = chartSensorService.get_sensor_data_reading(sensorId)
    return response