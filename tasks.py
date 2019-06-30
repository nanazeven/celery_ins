# -*- coding:utf-8 -*-
import pymongo
from celery import Celery,Task
from celery.utils.log import get_task_logger
from model.media import Media
from instagram_spider import InstagramSpider
import tools

app = Celery('tasks', broker='redis://@127.0.0.1:6379/2', backend='redis://@127.0.0.1:6379/3')
app.config_from_object('celeryconfig')


@app.task(bind=True)
def run_instabram_spider(self):
    client = pymongo.MongoClient(tools.MONGO_URI)
    collection = client[tools.MONGO_DB][tools.TARGET]
    inst = InstagramSpider(tools.USERNAME, tools.PASSWORD)
    inst.proxies = tools.PROXIES
    res = inst.get_medias(tools.TARGET)
    for i in res:
        print(i.dump())





# celery -A tasks worker -l info
# celery -A tasks beta -l info

