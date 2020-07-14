
from datetime import datetime, timedelta

def get_good_time_second(date):
    modSecond = date.second % 10
    if modSecond != 0:
        timeSecondRange = 10 - modSecond
        newDatetime = date + timedelta(seconds=timeSecondRange)
        return int(newDatetime.timestamp())
    return int(date.timestamp())
