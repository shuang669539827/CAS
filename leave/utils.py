#coding:utf8
import sys, urllib, urllib2, json
import requests
import logging
import time

errlog = logging.getLogger('daserr')
#apis.baidu.com

def getHoliday(info):
	print info
	url = 'http://apis.baidu.com/xiaogg/holiday/holiday?d=%s'%(info)
	headers = {"apikey":"a6cd14b29a20112d02350a133be393f0"}
	content = None
	for i in range(10):
		try:
			r = requests.get(url, headers=headers)
			content = r.text
			if type(json.loads(content)) == type(1):
				content = json.dumps({info:str(content)})
			elif type(json.loads(content)) == type({'a':1}):
				pass
			else:
				content = None
		except Exception, e:
			time.sleep(0.2)
		if content:
			break
	else:
		errlog.error('百度API异常,无法获取数据')
	print content,22
	return content


def getMonth(year, month, start_day, end_day, half=1):
	month_execpt_weekend = []
	month_apply_day = 0
	res = {}
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)

	info = ''
	if start_day == end_day:
		if start_day < 10:
			info = info + year_month + '0' + str(start_day) + ','
		else:
			info = info + year_month + str(start_day) + ','
	for day in  range(start_day, end_day+1):
		if day < 10:
			info = info + year_month + '0' + str(day) + ','
		else:
			info = info + year_month + str(day) + ','
	info = info.strip(',')

	result_json = getHoliday(info)
	result = json.loads(result_json)
	for k,v in result.items():
		if v == '0':
			month_apply_day = month_apply_day + 1
	if half == 0:
		month_apply_day = month_apply_day - 0.5
	res.update({'year_month': year_month, 'month_apply_day': month_apply_day})
	return res


def getMonthadd(year, month, start_day, end_day, half=1):
	month_execpt_weekend = []
	month_add_day = 0
	res = {}
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)

	info = ''
	if start_day == end_day:
		if start_day < 10:
			info = info + year_month + '0' + str(start_day) + ','
		else:
			info = info + year_month + str(start_day) + ','
	for day in  range(start_day, end_day+1):
		if day < 10:
			info = info + year_month + '0' + str(day) + ','
		else:
			info = info + year_month + str(day) + ','
	info = info.strip(',')

	result_json = getHoliday(info)
	result = json.loads(result_json)

	for k,v in result.items():
		if v != '0':
			month_add_day = month_add_day + 1
	if half == 0:
		month_add_day = month_add_day - 0.5
	res.update({'year_month': year_month, 'month_add_day': month_add_day})
	return res



if __name__ == "__main__":
	res = getMonth(2016,11,7,8,1)
	print res
	getHoliday('20170101')
