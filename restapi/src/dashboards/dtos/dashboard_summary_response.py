from schematics import Model
from schematics.types import StringType

class DashboardSummaryResponse(Model):
    id = StringType()
    name = StringType()
    color = StringType()
    createdAt = StringType()
    modifiedAt = StringType()