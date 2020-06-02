
from bson.objectid import ObjectId
from ..models.dtos.creating_dashboard_dto import CreatingDashboardDto
from ...shared.core.result import Result

class Option:
    def __init__(self, color: str):
        self.color = color

class Dashboard(Entity):
    def __init__(self, id: str, name: str, userId: str, option: Option):
        super.__init__(id)
        self.name = name
        self.userId = userId
        self.option = option
       
    def update(self, name: str, options: Option):
        super()
        self.name = name
        self.option = option

    @staticmethod
    def create(self, dto: CreatingDashboardDto) -> Result[Dashboard]:
        isMissingFields = dto.name == None
        if isMissingFields:
            return Result[Dashboard].fail("Create dashboard failed")
        return Result[Dashboard].ok(Dashboard(ObjectId(), name, userId, option))


