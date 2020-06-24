
from flask import Blueprint, request

from dashboards.ioc import init_dashboard_service

# Import middleware and Auth
from shared.middlewares.default_middleware import default_middleware
from shared.middlewares.request.permission.login import login_required

from dashboards.dtos.dashboard_dto import DashboardDto

# Init Dashboard Service
dashboardService = init_dashboard_service()

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

@dashboards_blueprint.route("/dashboard/<dashboardId>", methods=['GET'])
@default_middleware
@login_required()
def get(dashboardId: str):
    return dashboardService.get(dashboardId)

@dashboards_blueprint.route("/dashboard/<dashboardId>", methods=['PUT'])
@default_middleware
@login_required()
def update(dashboardId: str):
    body = request.get_json()
    dto = DashboardDto(body)
    response = dashboardService.updateNameAndOption(dashboardId, dto)
    return response

@dashboards_blueprint.route("/dashboard/<dashboardId>", methods=['DELETE'])
def delete(dashboardId: str):
    response = dashboardService.delete(dashboardId)
    return response
