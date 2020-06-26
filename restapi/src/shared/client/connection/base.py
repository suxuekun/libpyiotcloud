from shared.utils.singleton_util import Singleton


class IotDBConnection(metaclass=Singleton):
    def __init__(self):
        self._conn = None

    @property
    def conn(self):
        return self._conn