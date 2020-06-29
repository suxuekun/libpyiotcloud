from schematics.types import StringType

from shared.simple_api.dto import BaseDTO


class ProrateQueryDTO(BaseDTO):
    promocode = StringType(required=True)
    old_plan_id = StringType(required=True)
    new_plan_id = StringType(required=True)