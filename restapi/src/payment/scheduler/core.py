from apscheduler.schedulers.background import BackgroundScheduler
from shared.client.connection.mongo import DefaultMongoConnection
from payment.scheduler import config
from payment.scheduler.tasks import jobs

def init_scheduler():
    print('init scheduler')
    # 这里用于持久化的设置，代码中演示使用MongoDB
    # client用于设置你自己的MongoDB的handler, 即MongoClient对象
    client = DefaultMongoConnection().conn

    # using backgroundscheduler here
    scheduler = BackgroundScheduler(jobstores=config.jobstores, executors=config.executors, job_defaults=config.job_defaults, timezone=config.timezone)

    # clean old tasks
    client[config.db][config.collection].drop()

    # start scheduler
    scheduler.start()

    # create all tasks
    for job_id in jobs:
        job = jobs[job_id]
        print('--job', job_id, job)
        scheduler.add_job(job['task'],job['type'],**job['kwargs'],id=job_id)

    return scheduler