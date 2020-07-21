

from flask import Blueprint, request
from dashboards.dtos.chart_sensor_dto import ChartSensorDto
from shared.utils.query_param_util import get_boolean_value
from dashboards.dtos.chart_sensor_query import *
from dashboards.ioc import init_chart_sensor_service
from datetime import datetime
from dashboards.utils.time_util import get_good_time_second

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required
import json
chartSensorService = init_chart_sensor_service()

# Init routes
charts_sensor_blueprint = Blueprint('charts_sensor_blueprint', __name__)

@charts_sensor_blueprint.route("", methods=['POST'])
@default_middleware
@login_required()
def create(dashboardId: str):
    user = request.environ.get('user')
    body = request.get_json()
    dto = ChartSensorDto(body)
    response = chartSensorService.create(dashboardId, user["username"], dto)
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

    timestamp = int(queryParams.get(
        "timestamp", int(datetime.now().timestamp())))
    query.timestamp = get_good_time_second(datetime.fromtimestamp(timestamp))

    query.isMobile = get_boolean_value(
        queryParams.get("mobile", "false").lower())

    query.timeSpan = queryParams.get("timespan", 1)
    query.isRealtime = get_boolean_value(
        queryParams.get("realtime", "true").lower())

    query.selectedMinutes = []
    query.chartsId = []

    selectedMinutes = queryParams.get("selected_minutes", "")
    if selectedMinutes != "":
        parseSelectedMinutes = selectedMinutes.split(',')
        query.selectedMinutes = list(
            map(lambda i: int(i.strip()), parseSelectedMinutes))

    chartsId = queryParams.get("chartsId", "")
    if chartsId != "":
        parseChartsId = chartsId.split(",")
        query.chartsId = list(map(lambda i: i.strip(), parseChartsId))

    response = chartSensorService.gets(dashboardId, user["username"], query)
    return response

@charts_sensor_blueprint.route("/<chartId>", methods=['GET'])
@default_middleware
@login_required()
def get(dashboardId: str, chartId: str):
    user = request.environ.get('user')
    queryParams = request.args
    query = BaseChartSensorQuery()
    query.points = int(queryParams.get("points", 30))
    query.minutes = int(queryParams.get("minutes", 5))

    timestamp = int(queryParams.get(
        "timestamp", int(datetime.now().timestamp())))
    query.timestamp = get_good_time_second(datetime.fromtimestamp(timestamp))

    query.isMobile = get_boolean_value(
        queryParams.get("mobile", "false").lower())

    query.timeSpan = queryParams.get("timespan", 1)
    query.isRealtime = get_boolean_value(
        queryParams.get("realtime", "true").lower())

    response = chartSensorService.get(
        dashboardId, user["username"], chartId, query)
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
    query.timeSpan = int(queryParams.get("time_span", 1))

    timestamp = int(queryParams.get(
        "timestamp", int(datetime.now().timestamp())))
    query.timestamp = get_good_time_second(datetime.fromtimestamp(timestamp))

    query.isMobile = get_boolean_value(
        queryParams.get("mobile", "false").lower())

    query.timeSpan = queryParams.get("timespan", 1)
    query.isRealtime = get_boolean_value(
        queryParams.get("realtime", "true").lower())

    query.chartsId = []
    chartsId = queryParams.get("chartsId", "")
    if chartsId != "":
        parseChartsId = chartsId.split(",")
        query.chartsId = list(map(lambda i: i.strip(), parseChartsId))

    response = chartSensorService.compare(dashboardId, user["username"], query)
    return response
