import datetime
import json
from schematics import Model
from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType

from shared.core.model import BaseModel, TimeStampMixin, BaseIotModel
from shared.utils.schema_util import create_schema, model_to_json_schema

class Usage(Model):
    sms = DecimalType(default=0)
    email = IntType(default=0)
    notification = IntType(default=0)
    storage = IntType(default=0)  # count on MB 1000 up ?

class AbstractPlan(BaseIotModel,Usage):
    name = StringType()
    price = DecimalType()
    period = IntType()
    currency = StringType()

    def __str__(self):
        return self.name

    def is_free(self):
        return self.price <= 0


class Plan(AbstractPlan,TimeStampMixin,):
    bt_plan_id = StringType(max_length=255)
    active = BooleanType(default=True)

if __name__ == "__main__":
    plan = Plan.get_mock_object()
    raw = {
        'sms':10,
        'wtf':'wtf'
    }
    plan.import_data(raw)
    d = plan.to_primitive()
    t = d.get('createdAt')
    print (json.dumps(d, indent=4, sort_keys=True))# data
    print(plan.createdAt,t)
    print(datetime.datetime.fromtimestamp(t))
    print(datetime.datetime.utcfromtimestamp(t))
    # print (plan.validate())
    # print (plan.createdAt)
    # print (PlanModel._fields)
    # for i in PlanModel._fields.items():
    #     print (i)

    # a = ModelType(TestModel)

    # print(a.model_class)

    # print(Plan.testList.model_class)

    # ds = model_to_json_schema(Plan)
    # print(json.dumps(ds, indent=4, sort_keys=True)) # schema

