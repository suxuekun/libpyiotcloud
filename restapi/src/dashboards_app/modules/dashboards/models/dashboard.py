
from bson.objectid import ObjectId
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin
from dashboards_app.modules.dashboards.dtos.dashboard_dto import DashboardDto

class Option(BaseModel):
    color = StringType()

class DashboardModel(BaseModel, MongoIdMixin, TimeStampMixin):
    name = StringType()
    option = ModelType(Option)
    userId = StringType()
    gateways = ListType(StringType, default=[])
    sensors = ListType(StringType, default=[])
    actuators = ListType(StringType, default=[])

GATEWAYS = "GATEWAYS"
SENSORS = "SENSORS"

class Dashboard:

    def __init__(self, model: DashboardModel):
        self.model = model

    @staticmethod
    def create(userId: str, dto: DashboardDto):
        model = DashboardModel()
        model.name = dto.name
        model.userId = userId
        model.option = Option({'color': dto.color})
        model.gateways = []
        model.sensors = []
        model.actuators = []
        return Dashboard(model)

    def update_name_and_option(self, dto: DashboardDto):
        self.model.name = dto.name
        self.model.option = Option({'color': dto.color})

    def add_chart_gateway(self, chartId: str):
        self.model.gateways.append(chartId)
    
    def remove_chart_gateway(self, chartId: str):
        for id in self.model.gateways:
            if id == chartId:
                self.model.gateways.remove(id)
                return
    
    def addChartSensor(self, chartId: str):
        self.model.sensors.append(chartId)

    @staticmethod
    def to_domain(data):
        model = DashboardModel(data, strict=False)
        return Dashboard(model)
