

from dashboards_app.repositories.dashboard_repository import IDashboardRepository
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.models.dashboard import Dashboard, DashboardModel
from shared.core.response import Response
from shared.core.utils import JsonSchemaUtils

class DashboardService:
    def __init__(self, dashboardRepository: IDashboardRepository):
        self.dashboardRepository = dashboardRepository

    def create(self, dto: DashboardDto):

        dashboard = Dashboard.create(name=dto.name, color=dto.color)
        self.dashboardRepository.create(dashboard.model.to_primitive())

        return Response.success(True, "Create dashboard successfully")

    def updateNameAndOption(self, id: str, dto: DashboardDto):

        entity = self.dashboardRepository.getById(id)

        model = JsonSchemaUtils.create_model_schema(entity, _t)
        dashboard = Dashboard.toDomain(entity)

        dashboard.updateNameAndOption(name=dto.name, color=dto.color)

        self.dashboardRepository.update(id, dashboard.model.to_primitive())

        return Response.success(True, "Update dashboard successfully")
