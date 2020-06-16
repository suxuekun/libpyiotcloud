from schematics.types import ModelType, StringType, ListType
from shared.simple_api.dto import BaseDTO

class CheckoutItemDTO(BaseDTO):
    deviceid = StringType()


    pass

class CheckoutDTO(BaseDTO):
    nonce = StringType()
    items = ListType(ModelType(CheckoutItemDTO))
    pass