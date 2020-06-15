
from bson.objectid import ObjectId
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin
from dashboards_app.dtos.dashboard_dto import DashboardDto
from dashboards_app.dtos.chart_gateway_dto import ChartGatewayDto


class Option(BaseModel):
    color = StringType()

class DashboardDevice(BaseModel, MongoIdMixin):
    type = StringType(default="")

class ChartModel(BaseModel, TimeStampMixin):
    userId = StringType()
    dashboardId = StringType()
    device = ModelType(DashboardDevice)
    typeId = IntType()

    # Attribute is optional
    attributeId = IntType() 

class DashboardModel(BaseModel, MongoIdMixin, TimeStampMixin):
    name = StringType()
    option = ModelType(Option)
    userId = StringType()
    gateways = ListType(ModelType(ChartModel), default=[])
    sensors = ListType(ModelType(ChartModel), default=[])
    actuators = ListType(ModelType(ChartModel), default=[])

GATEWAYS = "GATEWAY"
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

    def add_chart_gateway(self, dto: ChartGatewayDto):
        chart = ChartModel()
        chart.userId = self.model.userId
        chart.dashboardId = self.model._id
        chart.device = DashboardDevice({"_id": dto.gatewayId, "type": GATEWAYS})
        chart.typeId = dto.chartTypeId
        chart.attributeId = dto.attributeId
        self.model.gateways.append(chart)
    
    def remove_chart_gateway(self, chartId: str):
        for chart in self.model.gateways:
            if chart._id == chartId:
                model.gateways.remove(chart)
                return
    
    def addChartSensor(self,  chart: ChartModel):
        self.model.sensors.append(chart)

    @staticmethod
    def to_domain(data):
        model = DashboardModel(data)
        return Dashboard(model)
