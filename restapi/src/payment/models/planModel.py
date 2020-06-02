import collections
import json

from schematics.types import StringType, DecimalType, IntType, BooleanType

from shared.core.model import BaseModel, TimeStampMixin
from shared.core.utils.JsonSchemaUtils import to_jsonschema, jsonschema_for_model


class PlanModel(BaseModel,TimeStampMixin):
    name = StringType()
    price = DecimalType()
    period = IntType()
    currency = StringType()

    sms = IntType()
    email = IntType()
    notification = IntType()
    storage = IntType()  # count on MB 1000 up ?

    bt_plan_id = StringType(max_length=255)
    active = BooleanType(default=True)


if __name__ == "__main__":
    plan = PlanModel()
    a = collections.OrderedDict()
    # print (plan.createdAt)
    # print (PlanModel._fields)
    # for i in PlanModel._fields.items():
    #     print (i)
    di = jsonschema_for_model(PlanModel)
    print(json.dumps(di, indent=4, sort_keys=True))

