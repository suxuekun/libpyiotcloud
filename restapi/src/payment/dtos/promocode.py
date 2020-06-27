from schematics.types import ModelType, StringType

from payment.models.promocode import AbstractPromo, AbstractPromoCode
from shared.simple_api.dto import BaseDTO


class PromoDTO(BaseDTO,AbstractPromo):
    pass

class PromoCodeDTO(BaseDTO,AbstractPromoCode):
    info = ModelType(PromoDTO)
    pass

class PromoCodeQueryDTO(BaseDTO):
    subscription_id = StringType(required=True)
    plan_id = StringType(required=True)

class PromoCodeVerifyDTO(BaseDTO):
    code = StringType(required=True)
    subscription_id = StringType(required=True)
    plan_id = StringType(required=True)
