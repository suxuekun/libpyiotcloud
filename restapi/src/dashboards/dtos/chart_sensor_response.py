
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType, FloatType
from dashboards.dtos.attribute_response import AttributeResponse

class MobileDatasetsSensorResponse(Model):
    # Timestamp
    x = IntType()   

    # Value of data
    y = FloatType()

    low = FloatType()
    high = FloatType()

class OldMobileDatasetSensorResponse(Model):
    fromTimestamp = IntType()
    toTimestamp = IntType()
    datasets = ListType(ModelType(MobileDatasetsSensorResponse))

    @staticmethod
    def create(fromTimestamp, toTimestamp, datasets: []):
        response = OldMobileDatasetSensorResponse()
        response.fromTimestamp = fromTimestamp
        response.toTimestamp = toTimestamp
        response.datasets = datasets

        return response

class DatasetsSensorResponse(Model):
    data = ListType(FloatType)
    labels = ListType(IntType)
    low = ListType(FloatType)
    high = ListType(FloatType)

class OldDatasetSensorResponse(DatasetsSensorResponse):
    fromTimestamp = IntType()
    toTimestamp = IntType()

    @staticmethod
    def create(fromTimestamp:int, toTimestamp:int, datasets: DatasetsSensorResponse):
        
        response = OldDatasetSensorResponse()
        response.fromTimestamp = fromTimestamp
        response.toTimestamp = toTimestamp
        response.data = datasets.data
        response.labels = datasets.labels
        response.low = datasets.low
        response.high = datasets.high

        return response

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
    gatewayUUID = StringType()
    gatewayName = StringType()
    minmax = ListType(StringType)
    accuracy = FloatType()
    unit = StringType()
    format = StringType()
    enabled = IntType()
    
class ChartSensorReponse(Model):
    id = StringType()
    chartTypeId = IntType()
    device = ModelType(SensorResponse)
    readings = ModelType(ReadingSensorResponse)
    selectedMinutes = IntType()

class WebChartSensorResponse(ChartSensorReponse):
    datasets = ModelType(DatasetsSensorResponse)
    oldDatasets = ListType(ModelType(OldDatasetSensorResponse))

class MobileChartSensorResponse(ChartSensorReponse):
    datasetsEx = ListType(ModelType(MobileDatasetsSensorResponse))
    oldDatasetsEx = ListType(ModelType(OldMobileDatasetSensorResponse))

