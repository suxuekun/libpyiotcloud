
from datetime import datetime


class TimestampUtil:
    @staticmethod
    def now():
        return str(datetime().utcnow().timestamp())
