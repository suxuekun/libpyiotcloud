
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType, FloatType
from dashboards.dtos.attribute_response import AttributeResponse


class DeviceResponse(Model):
    name = StringType()
    uuid = StringType()

# Dataset part

class DatasetResponse(Model):
    labels = ListType(StringType)
    data = ListType(FloatType)


class DatasetExResponse(Model):
    label = StringType()
    data = FloatType()

class ChartGatewayResponse(Model):
    attribute = ModelType(AttributeResponse)
    chartTypeId = IntType()
    id = StringType()
    device = ModelType(DeviceResponse)


class WebChartGatewayResponse(ChartGatewayResponse):
    datasets = ModelType(DatasetResponse)


class MobileChartGatewayResponse(ChartGatewayResponse):
    datasetsEx = ListType(ModelType(DatasetExResponse))


# Dataset Ex


class DatasetAttributeResponse(Model):
    labels = ListType(StringType)
    data = ListType(FloatType)
    filterId = IntType()
    filterName = StringType()

class DatasetExAttributeResponse(Model):
    filterId = IntType()
    filterName = StringType()
    values = ListType(ModelType(DatasetExResponse))


class ChartGatewayExResponse(Model):
    id = StringType()
    device = ModelType(DeviceResponse)
    chartTypeId = IntType()
    attribute = ModelType(AttributeResponse)

class WebChartGatewayExResponse(ChartGatewayExResponse):
    datasets = ListType(ModelType(DatasetAttributeResponse))

class MobileChartGatewayExResponse(ChartGatewayExResponse):
    datasetsEx = ListType(ModelType(DatasetExResponse))


