
from .....shared.core.usecase import UseCase
from ....models.dtos.creating_dashboard_dto import CreatingDashboardDto
from ....models.responses.creating_dashboard_response import creating_dashboard_response
from ....repositories.dashboard_repository import DashboardRepository
from .....shared.core.exceptions.created_exception import CreatedExeception
from .....shared.core.result import Result
from ....domains.dashboard import Dashboard


class CreateDashboardCommand(UseCase[CreatingDashboardDto, bool]):

    def __init__(self, dashboardRepo: DashboardRepository):
        self.dashboardRepo = dashboardRepo

    def build_usecase(self, input: CreatingDashboardDto) -> CreatingDashboardResponse:

        result = Dashboard.create(input)
        if result.is_failure:
            raise CreatedExeception

        self.dashboardRepo.create(result.get_value())
        return True
