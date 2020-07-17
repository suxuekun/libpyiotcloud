from schematics import Model
from schematics.types import BooleanType, StringType, UUIDType, IntType

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
    createdAt = IntType(default=timestamp_util.get_timestamp)
    modifiedAt = IntType(default=timestamp_util.get_timestamp)

class PeriodMixin(Model):
    start = IntType()
    end = IntType()

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
    start = IntType(default = timestamp_util.get_timestamp)
    end = IntType(default = timestamp_util.get_last_day_of_month_timestamp)


class DateMixin(Model):
    date = IntType()
    def set_now(self):
        # TODO
        pass

class ActiveMixin(Model):
    active = BooleanType(default=True)

class ActiveMixinDefaultFalse(Model):
    active = BooleanType(default=False)