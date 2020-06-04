
from flask import Blueprint, request


from dashboards_app.repositories.dashboard_repository import DashboardRepository
from dashboards_app.services.dashboard_service import DashboardService
from cached_mongo_client import CachedMongoClient
from dashboards_app.dtos.dashboard_dto import DashboardDto
service: DashboardService = None

def bootstrap():
    global service
    mongo_client = CachedMongoClient.get_instance().get_mongo_client()
    db = CachedMongoClient.get_instance().get_db()
    dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
    service = DashboardService(dashboardRepository)
    

# Init routes
dashboards_blueprint = Blueprint('dashboards_blueprint', __name__)

@dashboards_blueprint.route("", methods=['POST'])
def create_dashboard():
    body = request.get_json()
    dto = DashboardDto(body)
    response = service.create(dto)
    return response

@dashboards_blueprint.route("", methods=['GET'])
def get_dashboards():
    return service.getDashboards()

@dashboards_blueprint.route("/<id>", methods=['GET'])
def get_dashboardsDetail(id: str):
    return service.getDashboardDetail(id)

@dashboards_blueprint.route("/<id>", methods=['PUT'])
def getDetail(id: str):
    body = request.get_json()
    dto = DashboardDto(body)
    respnse = service.updateNameAndOption(id, dto)
    return respnse

@dashboards_blueprint.route("/charts", methods=['GET'])
def getCharts():
    print(service)
    dto = DashboardDto()
    dto.name = "Dashboard 1"
    dto.color = "Black"
    response = service.create(dto)
    return response, 200

