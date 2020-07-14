

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin
from dashboards.dtos.chart_gateway_dto import ChartGatewayDto
from bson.objectid import ObjectId
from dashboards.dtos.chart_sensor_dto import ChartSensorDto

GATEWAYS = "GATEWAYS"
SENSORS = "SENSORS"


class DashboardDevice(BaseModel):
    deviceUUID = StringType()
    type = StringType(default="")


class ChartModel(BaseModel, MongoIdMixin, TimeStampMixin):
    userId = StringType()
    dashboardId = StringType()
    deviceId = StringType()
    chartTypeId = StringType()


class ChartGatewayModel(ChartModel):
    attributeId = IntType()


class ChartSensorModel(ChartModel):
    pass


class ChartGateway:

    def __init__(self, model: ChartGatewayModel):
        self.model = model

    @staticmethod
    def create(dashboardId: str, userId: str, dto: ChartGatewayDto):
        model = ChartGatewayModel()
        model.userId = userId
        model.dashboardId = dashboardId
        model.deviceId = dto.deviceId
        model.chartTypeId = dto.chartTypeId
        model.attributeId = dto.attributeId
        return ChartGateway(model)


class ChartSensor:
    def __init__(self, model: ChartSensorModel):
        self.model = model

    @staticmethod
    def create(dashboardId: str, userId: str, dto: ChartSensorDto, sensorId: str):
        model = ChartSensorModel()
        model.userId = userId
        model.dashboardId = dashboardId
        model.deviceId = sensorId
        model.chartTypeId = dto.chartTypeId
        return ChartSensor(model)
