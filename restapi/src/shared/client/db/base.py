class IotDB():
    def __init__(self):
        self._db = None

    @property
    def db(self):
        return self._db