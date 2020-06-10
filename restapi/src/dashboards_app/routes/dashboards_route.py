
from flask import Blueprint, request


from dashboards_app.repositories.dashboard_repository import DashboardRepository
from dashboards_app.services.dashboard_service import DashboardService
from dashboards_app.dtos.dashboard_dto import DashboardDto
from shared.client.connection.mongo import DefaultMongoConnection
from shared.client.db.mongo.default import DefaultMongoDB
from shared.middlewares.request.permission.login import login_required
from dashboards_app.services.chart_type_service import ChartTypeService
from dashboards_app.repositories.chart_type_repository import ChartTypeRepository

#  Get config mongodb
mongo_client = DefaultMongoDB().conn
db = DefaultMongoDB().db

# Init Dashboard Service
service: DashboardService = None

dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
service = DashboardService(dashboardRepository)

# Init ChartTypeService
chartTypeService: ChartTypeService = None
chartTypeRepo = ChartTypeRepository(mongoclient=mongo_client, db = db, collectionName="chartTypes")
chartTypeService = ChartTypeService(chartTypeRepo)
chartTypeService.setup_chart_types()

# Init routes
dashboards_blueprint = Blueprint('dashboards_blueprint', __name__)

@dashboards_blueprint.route("", methods=['POST'])
@login_required()
def create():
    body = request.get_json()
    user = request.environ.get('user')
    dto = DashboardDto(body)
    response = service.create(user["username"], dto)
    return response

@dashboards_blueprint.route("", methods=['GET'])
@login_required()
def gets():
    user = request.environ.get('user')
    print(user)
    return service.gets(user["username"])

@dashboards_blueprint.route("/<id>", methods=['GET'])
@login_required()
def get(id: str):
    return service.get(id)

@dashboards_blueprint.route("/<id>", methods=['PUT'])
@login_required()
def update(id: str):
    body = request.get_json()
    dto = DashboardDto(body)
    response = service.updateNameAndOption(id, dto)
    return response

@dashboards_blueprint.route("/<id>", methods=['DELETE'])
@login_required()
def delete(id: str):
    response = service.delete(id)
    return response

@dashboards_blueprint.route("/charts/types/gateway", methods=['GET'])
def get_charrts_types_for_gateway():
    response = chartTypeService.gets_for_gateway()
    return response

@dashboards_blueprint.route("/charts/types/sensor", methods=['GET'])
def get_charts_tyoes_for_sensor():
    response = chartTypeService.gets_for_sensor()
    return response

