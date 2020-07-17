import datetime

from payment.scheduler.tasks.jobs.subscription_update import update_subscriptions_monthly
from shared.utils import timestamp_util


@timestamp_util.timing
def monthly_jobs():
    #monthly jobs here
    update_subscriptions_monthly()

jobs = {
    'monthly_scheduler':{
        'task':monthly_jobs,
        'type':'cron',
        # normal config
        'kwargs':{
            'month':'*',
            'day':'1',
            'hour':'0',
            'minute':"1",
        }
        # test config
        # 'kwargs':{
        #     'month':'*',
        #     'day':'*',
        #     'hour':'1',
        #     'minute':"12",
        # }
    }
}