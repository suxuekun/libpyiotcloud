

from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.models.dashboard import Dashboard
from shared.core.response import Response


class DashboardService:
    def __init__(self, dashboardRepository: IDashboardRepository):
        self.dashboardRepository = dashboardRepository

    def create(self, dto: DashboardDto):

        dashboard = Dashboard.create(name=dto.name, color=dto.color)

        dictDashboard = vars(dashboard)
        self.dashboardRepository.create(dictDashboard)

        return Response.success(True, "Create dashboard successfully")

    def updateNameAndOption(self, id: str, dto: DashboardDto):

        entity = self.dashboardRepository.getById(id)
        dashboard = Dashboard.toModel(id, entity)

        dashboard.updateNameAndOption(name=dto.name, color=dto.color)

        self.dashboardRepository.update(id, vars(dashboard))

        return Response.success(True, "Update dashboard successfully")
