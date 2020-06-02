import datetime

from schematics import Model
from schematics.types import DateTimeType, BooleanType


class BaseModel(Model):
    pass

class TimeStampMixin(Model):
    createdAt = DateTimeType(default=datetime.datetime.now)
    modifiedAt = DateTimeType(default=datetime.datetime.now)

class ActiveMixin(Model):
    active = BooleanType(default=True)

class ActiveMixinDefaultFalse(Model):
    active = BooleanType(default=False)