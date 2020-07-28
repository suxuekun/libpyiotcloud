import pytz
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from shared.client.connection.mongo import DefaultMongoConnection

db = "iot_scheduler"
collection = "payment_scheduler"
client = DefaultMongoConnection().conn
jobstores = {
    'default': MongoDBJobStore(client=client, database=db,collection=collection)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 5
}

timezone = pytz.timezone('US/Central')

if __name__ == "__main__":
    import datetime
    import tzlocal
    local_tz = tzlocal.get_localzone()
    print(local_tz)
    print('timezone',timezone,timezone)
    dt = datetime.datetime.now()
    offset = timezone.utcoffset(dt)
    print(offset)
    print(local_tz.utcoffset(dt))
    dt1 = datetime.datetime.now(timezone)
    print (dt1)