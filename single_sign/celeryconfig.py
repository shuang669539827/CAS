# -*- coding: utf-8 -*-
from __future__ import absolute_import
# from datetime import timedelta

# from django.conf import settings
from kombu import Queue, Exchange
from celery.schedules import crontab, timedelta


broker_url = 'redis://127.0.0.1/3'

# result_backend = 'redis://%s:%s/0' % (settings.REDIS_HOST, settings.REDIS_PORT)

# task_serializer = 'msgpack'

# result_serializer = 'json'

# result_expires = 60 * 60 * 8  # 结果过期时间

accept_content = ['json']  # 指定接受的内容类型

timezone = 'Asia/Shanghai'

enable_utc = True

ignore_result = True

worker_concurrency = 2

worker_prefetch_multiplier = 1

worker_max_tasks_per_child = 100

# worker_max_memory_per_child = 128 * 1024

# 指定导入的任务模块
imports = (
    'celerymail.tasks',
    'leave.tasks',
    'checkin.tasks',
)

beat_schedule = {
    'every-day-3-hour': {
        'task': 'checkin.input_sql_data',
        'schedule': crontab(minute=0, hour='3'),
        # 'schedule': timedelta(seconds=20),
        'args': ()
    },
    'every-day-4-hour': {
        'task': 'checkin.input_record',
        'schedule': crontab(minute=0, hour='4'),
        # 'schedule': timedelta(seconds=20),
        'args': ()
    },
    'every-day-5-hour': {
        'task': 'checkin.input_check_total',
        'schedule': crontab(0, 0, day_of_month='2'),
        # 'schedule': timedelta(seconds=20),
        'args': ()
    },
}

task_queues = (
    Queue('default'),
    Queue('msg', Exchange('taskfor_msg'), routing_key='taskfor_msg'),
    Queue('checkin', Exchange('checkin'), routing_key='checkin'),
    # Queue('hx', Exchange('taskfor_hx'), routing_key='taskfor_hx'),
    # Queue('scan', Exchange('taskfor_scan'), routing_key='taskfor_scan'),
)

task_create_missing_queues = True
task_default_exchange = 'default'
task_default_queue = 'default'  # 默认的队列, 如果一个消息不符合其他的队列就会放在默认队列里面
task_default_exchange_type = 'direct'
task_default_routing_key = 'task.default'


task_routes = {
    'celerymail.send_html_mail': {'queue': 'default'},
    'celerymail.send_msg': {'queue': 'msg', 'routing_key': 'taskfor_msg'},
    'checkin.input_sql_data': {'queue': 'checkin', 'routing_key': 'checkin'},
    'checkin.input_record': {'queue': 'checkin', 'routing_key': 'checkin'},
    'checkin.input_check_total': {'queue': 'checkin', 'routing_key': 'checkin'},
    # 'taskfor_scan': {'queue': 'scan', 'routing_key': 'taskfor_scan'},
}
