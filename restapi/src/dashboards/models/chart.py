

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
    device = ModelType(DashboardDevice)
    typeId = IntType()
    # Attribute is optional
    attributeId = IntType() 
    
class Chart:
    
    def __init__(self, model: ChartModel):
        self.model = model
        
    @staticmethod
    def create_for_gateway(dashboardId: str, userId: str, dto: ChartGatewayDto):
        model = ChartModel()
        model.userId = userId
        model.dashboardId = dashboardId
        model.device = DashboardDevice({"deviceUUID": dto.gatewayId, "type": GATEWAYS})
        model.typeId = dto.chartTypeId
        model.attributeId = dto.attributeId
        return Chart(model)
    
    @staticmethod
    def create_for_sensor(dashboardId: str, userId: str, dto: ChartSensorDto):
        model = ChartModel()
        model.userId = userId
        model.dashboardId = dashboardId
        model.device = DashboardDevice({"deviceUUID": dto.gatewayId, "type": SENSORS})
        model.typeId = dto.chartTypeId
        return Chart(model)