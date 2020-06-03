
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
    print(mongo_client)
    dashboardRepository = DashboardRepository(mongoclient=mongo_client, db = db, collectionName="dashboards")
    service = DashboardService(dashboardRepository)
    

# Init routes
dashboards_blueprint = Blueprint('dashboards_blueprint', __name__)


@dashboards_blueprint.route("/", methods=['POST'])
def createDashboard():
    body = request.get_json()
    print(body)
    return 'Hello', 200


@dashboards_blueprint.route("/<id>", methods=['GET'])
def getDetail(id: str):
    print(id)
    return 'OK', 200


@dashboards_blueprint.route("/charts", methods=['GET'])
def getCharts():
    print("Ok Service ne")
    print(service)
    dto = DashboardDto()
    dto.name = "Dashboard 1"
    dto.color = "Black"
    response = service.create(dto)
    return response, 200

