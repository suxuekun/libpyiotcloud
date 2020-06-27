from schematics.types import ModelType

from payment.models.promocode import AbstractPromo, AbstractPromoCode
from shared.simple_api.dto import BaseDTO


class PromoDTO(BaseDTO,AbstractPromo):
    pass

class PromoCodeDTO(BaseDTO,AbstractPromoCode):
    info = ModelType(PromoDTO)
    pass