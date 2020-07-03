
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType, FloatType
from dashboards.dtos.attribute_response import AttributeResponse

class DatasetSensorResponse(Model):
    data = ListType(FloatType)
    labels = ListType(IntType)
    low = ListType(FloatType)
    high = ListType(FloatType)

class ReadingSensorResponse(Model):
    highest = FloatType()
    lowest = FloatType()
    value = FloatType()

class SensorResponse(Model):
    id = StringType()
    source = StringType()
    number = IntType()
    sensorName = StringType()
    port = IntType()
    name = StringType()
    sensorClass = StringType()

class ChartSensorReponse(Model):
    id = StringType()
    chartTypeId = IntType()
    device = ModelType(SensorResponse)
    dataset = ModelType(DatasetSensorResponse)
    readings = ModelType(ReadingSensorResponse)
    
    