from functools import wraps

from shared.core.base_repository import BaseRepository
from shared.core.exceptions import S3Exception
from shared.core.repository.read_only import catch_throw_exception, ReadOnlyRepo
from shared.utils import dict_util

catch_s3_throw_error = catch_throw_exception(S3Exception)

class PaymentRepository(ReadOnlyRepo):
    def __init__(self, payment_client,*args,**kwargs):
        self.payment_client = payment_client
        self.raw = None
        super(PaymentRepository,self).__init__(self.raw,*args,**kwargs)