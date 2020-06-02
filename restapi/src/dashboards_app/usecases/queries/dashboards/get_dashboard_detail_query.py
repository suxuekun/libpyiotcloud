

from restapi.src.shared.core.usecase import UseCase
from restapi.src.dashboards_app.core.domains.dashboard import Dashboard
from restapi.src.dashboards_app.repositories.dashboard_repository import DashboardRepository
class GetDashboardDetailQuery(UseCase[str, Dashboard]):

    def __init__(self, dashboardRepo: DashboardRepository):
        self.dashboardRepo = dashboardRepo

    def build_usecase(self, id: str):
        result = self.dashboardRepo.getById(id)
        return super().build_usecase(input)