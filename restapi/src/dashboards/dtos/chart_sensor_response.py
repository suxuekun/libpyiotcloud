
from schematics import Model
from schematics.types import StringType, ModelType, IntType, ListType

class ChartSensorReponse(Model):
    typeId = IntType()
    id = StringType()