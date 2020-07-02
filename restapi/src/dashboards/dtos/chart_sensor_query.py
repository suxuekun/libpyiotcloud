
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from datetime import datetime


class ChartSensorQuery(Model):
    minutes = IntType()
    timestamp = IntType()
    points = IntType()


class ChartComparisonQuery(ChartSensorQuery):
    chartsId = ListType(StringType, min_size=2, max_size=3)
