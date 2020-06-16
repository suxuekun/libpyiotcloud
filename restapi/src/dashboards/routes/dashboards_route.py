
from flask import Blueprint, request

# Import config mongo
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB

# Import dashboards
from dashboards.repositories.dashboard_repository import DashboardRepository
from dashboards.services.dashboard_service import DashboardService
from dashboards.dtos.dashboard_dto import DashboardDto

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

