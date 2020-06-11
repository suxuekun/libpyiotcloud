from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType

class ChartGatewayDto(Model):
    gatewayId = StringType()
    attributeId = StringType()
    chartTypeId = StringType()