from payment.models.billing_address import AbstractBillingAddress
from shared.simple_api.dto import BaseDTO


class BillingAddressDTO(BaseDTO,AbstractBillingAddress):
    pass
