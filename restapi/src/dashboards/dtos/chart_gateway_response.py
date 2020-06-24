
from dashboards.models.gateway_attribute import AttributeValue
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType, FloatType

class DataSetResponse(Model): 
    labels = ListType(StringType)
    data = ListType(FloatType)

class AttributeResponse(Model):
    name = StringType()
    id = IntType()
    filters = ListType(ModelType(AttributeValue), default=[])

class DeviceResponse(Model):
    name = StringType()
    uuid = StringType()

class ChartGatewayResponse(Model):
    attribute = ModelType(AttributeResponse)
    datasets = ModelType(DataSetResponse)
    chartTypeId = IntType()
    id = StringType()
    device = ModelType(DeviceResponse)