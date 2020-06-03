import datetime
import json

from schematics.types import StringType, DecimalType, IntType, BooleanType, ListType, ModelType

from shared.core.model import BaseModel, TimeStampMixin
from shared.utils.schema_util import create_schema, model_to_json_schema


class TestModel(BaseModel):
    name = StringType()
    innerList = ListType(ListType(IntType))

class PlanModel(BaseModel, TimeStampMixin):
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
    testList = ListType(ListType(ModelType(TestModel)))
    testList2 = ListType(ListType(IntType))
    testModel3 = ModelType(TestModel)
    testListModel = ListType(ModelType(TestModel))



    def update(self, name):
        self.name = 'dasd'

if __name__ == "__main__":
    plan = PlanModel()
    plan.testList = [[TestModel(),TestModel()]]
    plan.testList2 = [[1,2]]
    d = plan.to_primitive()
    t = d.get('createdAt')
    print (json.dumps(d, indent=4, sort_keys=True))// data
    print(plan.createdAt)
    print(datetime.datetime.fromtimestamp(t))
    print(datetime.datetime.utcfromtimestamp(t))
    # print (plan.validate())
    # print (plan.createdAt)
    # print (PlanModel._fields)
    # for i in PlanModel._fields.items():
    #     print (i)

    # a = ModelType(TestModel)

    # print(a.model_class)

    # print(PlanModel.testList.model_class)

    ds = model_to_json_schema(PlanModel)
    print(json.dumps(ds, indent=4, sort_keys=True)) // schema

