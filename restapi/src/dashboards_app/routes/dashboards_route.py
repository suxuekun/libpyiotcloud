
from flask import Blueprint, request


from dashboards_app.repositories.dashboard_repository import DashboardRepository
from dashboards_app.services.dashboard_service import DashboardService
from shared.services.cached_mongo_client_service import CachedMongoClientService

#  Init injection
dashboardRepository = DashboardRepository(
    mongoclient=CachedMongoClientService.get_instacne().get_mongo_client(), collection="dashboards")
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
def getCharts(id: str):
    print(id)
    return 'OK', 200

