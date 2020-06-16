
from typing import List

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType
from shared.core.model import BaseModel, TimeStampMixin, MongoIdMixin

STORAGE_USAGE = "Storage Usage"
STORAGE_USAGE_ID = 0

ON_OFF_LINE = "On-line/Offline status"
ON_OFF_LINE_ID = 1

COUNT_OF_ALERTS = "Count of alerts"
COUNT_OF_ALERTS_ID = 2


class AttributeValue(BaseModel):
    name = StringType()
    id = IntType()

class GatewayAttributeModel(BaseModel, TimeStampMixin):
    name = StringType()
    _id = IntType()
    lables = ListType(ModelType(AttributeValue), default=[])
    filters = ListType(ModelType(AttributeValue), default=[])

class FactoryGatewayAttribute:

    @staticmethod
    def create(name: str):
        if name == STORAGE_USAGE:
            return StorageUsageAttribute.create()
        if name == ON_OFF_LINE:
            return OnOffLineStatusAttribute.create()
        if name == COUNT_OF_ALERTS:
            return CountOfAlertsAttribute.create()
        return GatewayAttributeModel()

# LABELS
USED_STORAGE_VALUE = "Used"
USED_STORAGE_ID = 0

FREE_STORAGE_VALUE = "Free"
FREE_STORAGE_ID = 1


class StorageUsageAttribute(GatewayAttributeModel):

    @staticmethod
    def create():
        model = GatewayAttributeModel()
        model._id = STORAGE_USAGE_ID
        model.name = STORAGE_USAGE
        model.lables = [
            AttributeValue({"id": USED_STORAGE_ID, "name": USED_STORAGE_VALUE}),
            AttributeValue({"id": FREE_STORAGE_ID, "name": FREE_STORAGE_VALUE})
        ]
        model.filters = []
        return model


# Labels
ONLINE_VALUE = "Online"
ONLINE_ID = 0

OFFLINE_VALUE = "Offline"
OFFLINE_ID = 1

# Filters
ONE_DAY_VALUE = "1 Day"
ONE_DAY_ID = 0

ONE_WEEK_VALUE = "1 Week"
ONE_WEEK_ID = 1

ONE_MONTH_VALUE = "1 Month"
ONE_MONTH_ID = 2


class OnOffLineStatusAttribute(GatewayAttributeModel):

    @staticmethod
    def create():
        model = GatewayAttributeModel()
        model._id = ON_OFF_LINE_ID
        model.name = ON_OFF_LINE
        model.lables = [
            AttributeValue({"id": ONLINE_ID, "name": ONLINE_VALUE}),
            AttributeValue({"id": OFFLINE_ID, "name": OFFLINE_VALUE})
        ]
        model.filters = [
            AttributeValue({"id": ONE_DAY_ID, "name": ONE_DAY_VALUE}),
            AttributeValue({"id": ONE_WEEK_ID, "name": ONE_WEEK_VALUE}),
            AttributeValue({"id": ONE_MONTH_ID, "name": ONE_MONTH_VALUE}),
        ]
        return model


# Labels
SENT_VALUE = "Sent"
SENT_ID = 0

REMAINING_VALUE = "Remaining"
REMAINING_ID = 1

# Filters
SMS_VALUE = "SMS"
SMS_ID = 0

EMAILS_VALUE = "EMAILS"
EMAILS_ID = 1

NOTIFICATIONS_VALUE = "NOTIFICATIONS"
NOTIFICATIONS_ID = 2


class CountOfAlertsAttribute(GatewayAttributeModel):

    @staticmethod
    def create() -> GatewayAttributeModel:
        model = GatewayAttributeModel()
        model._id = COUNT_OF_ALERTS_ID
        model.name = COUNT_OF_ALERTS
        model.lables = [
            AttributeValue({"id": SENT_ID, "name": SENT_VALUE}),
            AttributeValue({"id": REMAINING_ID, "name": REMAINING_VALUE})
        ]
        model.filters = [
            AttributeValue({"id": SMS_ID, "name": SMS_VALUE}),
            AttributeValue({"id": EMAILS_ID, "name": EMAILS_VALUE}),
            AttributeValue(
                {"id": NOTIFICATIONS_ID, "name": NOTIFICATIONS_VALUE})
        ]
        return model
