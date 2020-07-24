from schematics import Model
from schematics.types import StringType, IntType

class DashboardSummaryResponse(Model):
    id = StringType()
    name = StringType()
    color = StringType()
    createdAt = StringType()
    modifiedAt = StringType()
    totalGateways = IntType()
    totalSensors = IntType()
    totalActuators = IntType()