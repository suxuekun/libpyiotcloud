from payment.models.transaction import AbstractTransaction
from shared.simple_api.dto import BaseDTO


class TransactionDTO(BaseDTO,AbstractTransaction):
    pass