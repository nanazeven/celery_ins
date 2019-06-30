# -*- coding:utf-8 -*-
from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'ptask': {
        'task': 'tasks.run_instabram_spider',
        'schedule': crontab(hour=7, minute=30),
        # 'schedule': timedelta(seconds=36000),
    },
}
CELERY_RESULT_BACKEND = 'redis://@127.0.0.1:6379/3'