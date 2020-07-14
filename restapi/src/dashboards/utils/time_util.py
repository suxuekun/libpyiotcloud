
from datetime import datetime, timedelta

def get_good_time_second(date):
    modSecond = date.second % 10
    if modSecond != 0:
        newDatetime = date - timedelta(seconds=modSecond)
        return int(newDatetime.timestamp())
    return int(date.timestamp())
