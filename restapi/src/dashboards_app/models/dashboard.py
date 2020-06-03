
from shared.core.base_model import BaseModel, WithCreatedTimestamp, WithUpdatedTimeStamp
from bson.objectid import ObjectId
from dashboards_app.models.gateway_attribute import GatewayAttribute
from shared.utils.timestamp_util import TimestampUtil

class Option:
    def __init__(self, color: str):
        self.color = color


class DashboardDevice(BaseModel):
    type: str


class Chart(BaseModel, WithCreatedTimestamp):
    userId: str
    dashboardId: str
    device: DashboardDevice
    chartTypeId: str
    attribute: GatewayAttribute

class DashboardModel(BaseModel, WithCreatedTimestamp, WithUpdatedTimeStamp):
    name: str
    option: Option
    gateways: []
    sensors: []

class Dashboard:

    def __init__(self, model: DashboardModel):
        self.model = model

    @staticmethod
    def create(self, name: str, color: str):
        model = DashboardModel()
        model._id = ObjectId()
        model.option = Option(color)
        model.createdAt = TimestampUtil.now()
        model.updatedAt = TimestampUtil.now()
        model.sensors = []
        model.gateways = []
        return Dashboard(model)

    def updateNameAndOption(self, name: str, color: str):
        self.model.name = name
        self.model.option = Option(color)

    def addChartGateway(self, chart: Chart):
        self.model.gateways.append(chart)

    def addChartSensor(self,  chart: Chart):
        self.model.sensors.append(chart)

    # @staticmethod
    # def toModel(self, id, data: {}):
    #     return Dashboard(id, data)