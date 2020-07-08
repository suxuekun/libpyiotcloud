from functools import wraps

from shared.core.base_repository import BaseRepository
from shared.core.exceptions import S3Exception
from shared.core.repository.read_only import catch_throw_exception, ReadOnlyRepo
from shared.utils import dict_util

catch_s3_throw_error = catch_throw_exception(S3Exception)

class S3Repository(ReadOnlyRepo):
    def __init__(self, s3_client,file_name,*args,**kwargs):
        self.s3_client = s3_client
        self.file_name = file_name
        self.raw = None
        super(S3Repository,self).__init__(self.raw,*args,**kwargs)
        self.reload()

    def reload(self):
        print('s3-reload')
        self.raw = self.s3_client.get_raw_file_bytes(self.file_name)
        self._handler(self.raw)

    def _handler(self,raw):
        print('--s3-- handler not impl',raw)
        pass