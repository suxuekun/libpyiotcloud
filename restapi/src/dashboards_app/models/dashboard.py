
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


class Dashboard(BaseModel, WithCreatedTimestamp, WithUpdatedTimeStamp):

    name: str
    option: Option
    gateways: []
    sensors: []

    def __init__(self, props: {}):
        super().__init__(id)
        self.name = props["name"]
        self.option = props["options"]
        self.createdAt = props["createdAt"]
        self.updatedAt = props["updatedAt"]
        self.gateways = props["gateways"] != None and props["gateways"] or []
        self.sensors = props["sensors"] != None and props["sensors"] or []
        
    @staticmethod
    def create(self, name: str, color: str):
        props = {
            "name": name,
            "option": Option(color),
            "createdAt": TimestampUtil.now(),
            "updatedAt": TimestampUtil.now(),
            "sensors": [],
            "gateways": []
        }
        return Dashboard(ObjectId(), props)

    def updateNameAndOption(self, name: str, color: str):
        self.name = name
        self.option = Option(color)

    def addChartGateway(self, chart: Chart):
        self.gateways.append(chart)

    def addChartSensor(self,  chart: Chart):
        self.sensors.append(chart)

    @staticmethod
    def toModel(self, id, data: {}):
        return Dashboard(id, data)
