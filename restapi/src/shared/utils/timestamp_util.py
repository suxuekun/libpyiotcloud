from datetime import datetime, timezone, timedelta
import time
import calendar

def get_timestamp_float():
    return datetime.now().timestamp()

def get_timestamp_int():
    return int(get_timestamp_float())

def get_timestamp():
    return str(int((datetime.now().timestamp())))

def totalday_of_month(from_date=None):
    from_date = from_date or datetime.now()
    total_days = calendar.monthrange(from_date.year, from_date.month)[1]
    return total_days

def get_first_day_of_month(from_date = None):
    from_date = from_date or datetime.now()
    res_date = from_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return res_date

def get_first_day_of_month_timestamp(from_date = None):
    return str(int(get_first_day_of_month(from_date).timestamp()))

def get_next_month_first_day(from_date = None):
    from_date = from_date or datetime.now()
    days_in_month = lambda dt: calendar.monthrange(dt.year, dt.month)[1]
    next_month_first_day = from_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days_in_month(from_date))
    return next_month_first_day

def get_next_month_first_day_timestamp(from_date = None):
    next_month_first_day = get_next_month_first_day(from_date)
    return str(int(next_month_first_day.timestamp()))

def get_last_day_of_month(from_date = None):
    next_month_first_day = get_next_month_first_day(from_date)
    res_date = next_month_first_day - timedelta(seconds=1)
    return res_date

def get_last_day_of_month_timestamp(from_date = None):
    return str(int(get_last_day_of_month(from_date).timestamp()))



def remaining_days_of_month(from_date=None):
    from_date = from_date or datetime.now()
    total_days = totalday_of_month()
    return total_days - from_date.day + 1

def percent_of_month_left(from_date=None):
    from_date = from_date or datetime.now()
    total_days = totalday_of_month(from_date)
    remaining_days = total_days - from_date.day + 1
    return remaining_days/total_days,remaining_days,total_days

def datetime_from_string(date_string,string_format = '%m/%d/%Y'):
    return datetime.strptime(date_string,string_format)

def timestamp_from_date_string(date_string,string_format = '%m/%d/%Y'):
    d = datetime_from_string(date_string,string_format)
    return str(int(d.timestamp()))

if __name__ == "__main__":
    r = percent_of_month_left()
    print (r)

if __name__ == "__main__":
    d_now = datetime.now()# get local time naive time , no time zone awared
    d_utc = datetime.utcnow()# get local time as utc time // bug or feature ? this utc time is no time zone awared!!!
    correct_utc = d_utc.replace(tzinfo=timezone.utc)

    timestamp_from_now = d_now.timestamp()#this is real unix timestamp
    timestamp_from_utc = d_utc.timestamp()#this is not correct unix timestamp , this is utc time using local time zone problem
    timestamp_correct = correct_utc.timestamp()#this is correct unix timestamp,utc time using utc timezone,you need to manually assign utc time to a utcnow()!!!
    print(timestamp_from_now,timestamp_from_utc,timestamp_correct)

    dt1 = datetime.fromtimestamp(timestamp_from_now)## current local time correct
    dt2 = datetime.fromtimestamp(timestamp_from_utc)## current local time wrong
    dt3 = datetime.utcfromtimestamp(timestamp_from_now)## current utc time correct
    dt4 = datetime.utcfromtimestamp(timestamp_from_utc)## current utc time wrong

    print('dt1 local time', dt1,dt1.tzinfo)# current local time correct
    print('dt2 local time', dt2,dt2.tzinfo)# current local time wrong
    print('dt3 utc time ', dt3,dt3.tzinfo)# current utc time correct
    print('dt4 utc time', dt4,dt4.tzinfo)# current utc time wrong

    print('utc time shoule like this:',correct_utc,correct_utc.tzinfo)

    print('concolution:',)
    print('use datetime.now().timestamp() to get correct unix timestamp')
    print('use datetime.fromtimestamp(timestamp) to get current local time')
    print('use datetime.utcfromtimestamp(timestamp) to get current utc time, this time is also no timezone awared, just naive time , so use carefully')
    print('unless you have a global time setting for the whole project')

    print('also int(time.time()) is same with int(datetime.now().timestamp())')
    print('int(time.time()) = ',int(time.time()),'int(datetime.now().timestamp()) =',int(datetime.now().timestamp()))

    # print(d_now.strftime("%Y-%m-%d %H %M %S"))
    sd = datetime.strptime('7/1/2018','%m/%d/%Y')
    print (sd.timestamp())

    print (d_now.month)

    d2_now = datetime.now()

    d2_now = d_now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    last_day = get_last_day_of_month_timestamp()
    print(d2_now,last_day)

    next_first_day = get_next_month_first_day()
    next_last_day = get_last_day_of_month(next_first_day)
    print(next_first_day,next_last_day)

    next_month_first_day_timestamp = get_next_month_first_day_timestamp()
    next_month_last_day_timestamp = get_last_day_of_month_timestamp(next_first_day)

    print(next_month_first_day_timestamp,next_month_last_day_timestamp)

    print(datetime.fromtimestamp(int(next_month_first_day_timestamp)),datetime.fromtimestamp(int(next_month_last_day_timestamp)))




