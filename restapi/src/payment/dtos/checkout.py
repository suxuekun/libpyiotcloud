from schematics.types import ModelType, StringType, ListType
from shared.simple_api.dto import BaseDTO

class CheckoutItemDTO(BaseDTO):
    subscription_id = StringType()
    plan_id = StringType()
    promocode = StringType()
    pass

class CheckoutDTO(BaseDTO):
    nonce = StringType()
    items = ListType(ModelType(CheckoutItemDTO))
    pass