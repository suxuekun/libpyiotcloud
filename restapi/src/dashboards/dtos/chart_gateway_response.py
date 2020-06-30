
from dashboards.models.gateway_attribute import AttributeValue
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType, FloatType

class DatasetResponse(Model): 
    labels = ListType(StringType)
    data = ListType(FloatType)
    filterId = IntType()
    filterName = StringType()

class DatasetExResponse(Model):
    label = StringType()
    data = IntType()

class AttributeResponse(Model):
    name = StringType()
    id = IntType()
    filters = ListType(ModelType(AttributeValue), default=[])

class DeviceResponse(Model):
    name = StringType()
    uuid = StringType()


class DatasetAttributeResponse(Model):
    labels = ListType(StringType)
    data = ListType(FloatType)
    filterId = IntType()
    filterName = StringType()

class DatasetExAttributeResponse(Model):
    filterId = IntType()
    filterName = StringType()
    values =  ListType(ModelType(DatasetExResponse))

class ChartGatewayExResponse(Model):
    id = StringType()
    device = ModelType(DeviceResponse)
    chartTypeId = IntType()
    attribute = ModelType(AttributeResponse)
    datasets = ListType(ModelType(DatasetAttributeResponse))
    datasetsEx = ListType(ModelType(DatasetExAttributeResponse))
    
class ChartGatewayResponse(Model):
    attribute = ModelType(AttributeResponse)
    datasets = ModelType(DatasetResponse)
    datasetsEx = ListType(ModelType(DatasetExResponse))
    chartTypeId = IntType()
    id = StringType()
    device = ModelType(DeviceResponse)