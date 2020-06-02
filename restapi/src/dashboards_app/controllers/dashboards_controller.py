
from ..repositories.dashboard_repository import DashboardRepository
from ..usecases.commands.dashboards.create_dashboard_command import CreateDashboardCommand
from flask import Blueprint, request

dashboards_controller = Blueprint('dashboards_controller', __name__)


# # define repositories
dashboardRepo = DashboardRepository()

# # define commands
createDashboardCommand = CreateDashboardCommand(dashboardRepo)

# define queries

# define routes

@dashboards_controller.route("/", methods=['POST'])
def createDashboard():
    body = request.get_json()
    print(body)
    return 'Hello', 200

@dashboards_controller.route("/<id>", methods=['GET'])
def getDetail(id: str):
    print(id)
    return 'OK', 200
