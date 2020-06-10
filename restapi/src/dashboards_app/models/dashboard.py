
from bson.objectid import ObjectId
from dashboards_app.models.gateway_attribute import GatewayAttributeModel
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin
from dashboards_app.dtos.dashboard_dto import DashboardDto
from schematics import Model

class Option(BaseModel):
    color = StringType()

class DashboardDevice(BaseModel):
    type = StringType(default="")

class Chart(BaseModel, TimeStampMixin):
    userId = StringType()
    dashboardId = StringType()
    device = ModelType(DashboardDevice)
    chartTypeId = StringType()
    attribute = StringType()

class DashboardModel(BaseModel, MongoIdMixin, TimeStampMixin):
    name = StringType()
    option = ModelType(Option)
    userId = StringType()
    gateways = ListType(ModelType(Chart), default=[])
    sensors = ListType(ModelType(Chart), default=[])
    actuators = ListType(ModelType(Chart), default=[])
    
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

    def updateNameAndOption(self, dto: DashboardDto):
        self.model.name = dto.name
        self.model.option = Option({'color': dto.color})
    
    def addChartGateway(self, chart: Chart):
        self.model.gateways.append(chart)

    def addChartSensor(self,  chart: Chart):
        self.model.sensors.append(chart)

    @staticmethod
    def toDomain(data):
        model = DashboardModel(data)
        return Dashboard(model)
