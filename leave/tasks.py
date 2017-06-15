# -*- coding:utf-8 -*-
from __future__ import absolute_import, division
import datetime
import math

from celery import current_app as app
from celery.utils.log import get_task_logger

from leave.models import UserHoliday


logger = get_task_logger(__name__)


@app.task(name='celerymail.flash_annual', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def flash_annual():
    logger.info('celerymail.flash_annual')
    now = datetime.date.today()
    for obj in UserHoliday.objects.all():
        in_time = obj.user.pro.in_time
        if not in_time:
            logger.info(obj.user.first_name + 'has no in_time')
            continue
        if now.year == in_time.year:
            work_days = (now - in_time).days
        else:
            work_days = datetime.datetime.now().timetuple()[7]

        if obj.user.pro.work_year < 1:
            can_use_day = 0.0
        elif obj.user.pro.work_year < 10:
            can_use_day = round((work_days/365) * 5, 1)
        elif obj.user.pro.work_year < 20:
            can_use_day = round((work_days/365) * 10, 1)
        else:
            can_use_day = round((work_days/365) * 15, 1)

        fractional, integer = math.modf(can_use_day)
        if 0 < fractional < 0.4:
            obj.can_use_day = integer
        elif 0.4 <= fractional < 0.8:
            obj.can_use_day = integer + 0.5
        else:
            obj.can_use_day = integer + 1
        obj.save()
