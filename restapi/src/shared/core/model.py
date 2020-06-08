import datetime

from schematics import Model
from schematics.types import DateTimeType, BooleanType, TimestampType, StringType

from shared.utils import timestamp_util

class BaseModel(Model):
    pass

class MongoIdMixin(Model):
    _id = StringType()
    pass

class TimeStampMixin(Model):
    createdAt = TimestampType(default=timestamp_util.get_timestamp)
    modifiedAt = TimestampType(default=timestamp_util.get_timestamp)

class ActiveMixin(Model):
    active = BooleanType(default=True)

class ActiveMixinDefaultFalse(Model):
    active = BooleanType(default=False)