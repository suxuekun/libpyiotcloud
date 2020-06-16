import datetime
from bson.objectid import ObjectId

from schematics import Model
from schematics.types import DateTimeType, BooleanType, TimestampType, StringType

from shared.utils import timestamp_util

class BaseModel(Model):
    pass

class MongoIdMixin(Model):
    _id = StringType()
    pass

    
class TimeStampMixin(Model):
    createdAt = StringType(default=timestamp_util.get_timestamp)
    modifiedAt = StringType(default=timestamp_util.get_timestamp)

class ActiveMixin(Model):
    active = BooleanType(default=True)

class ActiveMixinDefaultFalse(Model):
    active = BooleanType(default=False)