
from dashboards.models.gateway_attribute import AttributeValue
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType

class DataSetResponse(Model): 
    id = StringType()
    name =  StringType()
    value = StringType()

class AttributeResponse(Model):
    name = StringType()
    id = IntType()
    filters = ListType(ModelType(AttributeValue), default=[])

class ChartGatewayResponse(Model):
    attribute = ModelType(AttributeResponse)
    datasets = ListType(ModelType(DataSetResponse), default=[])
    typeId = IntType()
    id = StringType()
    deviceName = StringType()
    deviceUUID = StringType()