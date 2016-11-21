#!/usr/bin/python
#-*- coding:utf-8 -*-
from __future__ import absolute_import
import datetime

from celery import current_app as app
from leave.models import MonthApply, UserHoliday
from cas.models import Pro
from django.contrib.auth.models import User


# month_num = 0
# year_num = 0

@app.task(name='task_month')
def month():
	year = datetime.datetime.now().year
	month = datetime.datetime.now().month
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)
	users = User.objects.all()
	for user in users:
		try:
			MonthApply.objects.get(user=user, year_month=year_month)
		except MonthApply.DoesNotExist:
			MonthApply.objects.create(user=user, year_month=year_month)
		


@app.task(name='task_year')
def year():
	objs = Pro.objects.all()
	for obj in objs:
		obj.work_year = obj.work_year + 1
		obj.save()
	users = User.objects.exclude(username='cas')
	for user in users:
		holiday_obj = UserHoliday.objects.get(user=user)
		if user.pro.work_year < 1:
			holiday_obj.year_day = 0
		elif user.pro.work_year < 10:
			holiday_obj.year_day = 5
		elif user.pro.work_year < 20:
			holiday_obj.year_day = 10
		else:
			holiday_obj.year_day = 15
		holiday_obj.save()


