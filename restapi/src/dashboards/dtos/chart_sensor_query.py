
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from datetime import datetime
from dashboards.exceptions.chart_sensor_query_exception import ChartSensorQueryException

class ChartSensorQuery(Model):
    minutes = IntType()
    timestamp = IntType()
    points = IntType()

    def validate(self, partial=False, convert=True, app_data=None, **kwargs):
        super().validate(partial=partial, convert=convert, app_data=app_data, **kwargs)
        if self.points != 30 and self.points != 60:
            raise ChartSensorQueryException("Points should be 30 or 60 points")


class ChartComparisonQuery(ChartSensorQuery):
    chartsId = ListType(StringType, min_size=2, max_size=3)
