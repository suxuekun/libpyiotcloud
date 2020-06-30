import datetime
import uuid

from bson import ObjectId
from schematics import Model
from schematics.types import DateTimeType, BooleanType, TimestampType, StringType, UUIDType

from shared.utils import timestamp_util

class BaseModel(Model):
    pass

class UUIDMixin(Model):
    _id = UUIDType()

class MongoIdMixin(Model):
    _id = StringType()


class BaseMongoModel(BaseModel,MongoIdMixin):
    pass

class BaseIotModel(BaseMongoModel):
    pass

class UserMixin(Model):
    username = StringType()

class DeviceMixin(Model):
    deviceid = StringType()
    devicename = StringType()

class TimeStampMixin(Model):
    createdAt = StringType(default=timestamp_util.get_timestamp)
    modifiedAt = StringType(default=timestamp_util.get_timestamp)

class PeriodMixin(Model):
    start = StringType()
    end = StringType()

    def set_this_month(self):
        #TODO
        pass
    def set_now_to_month_end(self):
        #TODO
        pass
    def set_this_year(self):
        # TODO
        pass
    def set_now_to_year_end(self):
        # TODO
        pass

class MonthPeriodMixin(PeriodMixin):
    start = StringType(default = timestamp_util.get_timestamp)
    end = StringType(default = timestamp_util.get_last_day_of_month_timestamp)


class DateMixin(Model):
    date = StringType()
    def set_now(self):
        pass

class ActiveMixin(Model):
    active = BooleanType(default=True)

class ActiveMixinDefaultFalse(Model):
    active = BooleanType(default=False)