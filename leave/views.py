#coding:utf8
from __future__ import unicode_literals
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404, StreamingHttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
#from django.core.mail import send_mail

from .forms import ApplyForm, VisitForm, MaterForm, FileForm
from .models import Apply, UserHoliday, MonthApply, LeaveType
from .utils import getMonth, getMonthadd
from cas.views import send_mail
from django.views.generic import ListView
from django.core.paginator import Paginator
from cas.models import Pro
from xlwt import * 

import StringIO
import logging
import datetime
import time
import traceback
import calendar
import csv
import smtplib
import codecs
import re
import os

# Create your views here.


errlog = logging.getLogger('daserr')
# leap = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
# nleap = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
api_res = {u'20170630': u'0', u'20170730': u'1', u'20170731': u'0', u'20161208': u'0', u'20161209': u'0', u'20161206': u'0', u'20161207': u'0', u'20161204': u'1', u'20161205': u'0', u'20161202': u'0', u'20161203': u'1', u'20161201': u'0', u'20171226': u'0', u'20171018': u'0', u'20171019': u'0', u'20171016': u'0', u'20171017': u'0', u'20170831': u'0', u'20171015': u'1', u'20171012': u'0', u'20171013': u'0', u'20171010': u'0', u'20171011': u'0', u'20171202': u'1', u'20171201': u'0', u'20170402': u'1', u'20170403': u'0', u'20171206': u'0', u'20170401': u'1', u'20170406': u'0', u'20170407': u'0', u'20170404': u'0', u'20170405': u'0', u'20171207': u'0', u'20170408': u'1', u'20170409': u'1', u'20170311': u'1', u'20170929': u'0', u'20170928': u'0', u'20170925': u'0', u'20170924': u'1', u'20170927': u'0', u'20170926': u'0', u'20170921': u'0', u'20170920': u'0', u'20170923': u'1', u'20170922': u'0', u'20170119': u'0', u'20170716': u'1', u'20170205': u'1', u'20170206': u'0', u'20170207': u'0', u'20170712': u'0', u'20170713': u'0', u'20170710': u'0', u'20170711': u'0', u'20170208': u'0', u'20170209': u'0', u'20170718': u'0', u'20170719': u'0', u'20170811': u'0', u'20170810': u'0', u'20170813': u'1', u'20170812': u'1', u'20170815': u'0', u'20170814': u'0', u'20170817': u'0', u'20170816': u'0', u'20170819': u'1', u'20170818': u'0', u'20170302': u'0', u'20171219': u'0', u'20161129': u'0', u'20161128': u'0', u'20170518': u'0', u'20170519': u'0', u'20170708': u'1', u'20170510': u'0', u'20170511': u'0', u'20170512': u'0', u'20170513': u'1', u'20170514': u'1', u'20170515': u'0', u'20170516': u'0', u'20170517': u'0', u'20171108': u'0', u'20171109': u'0', u'20170527': u'1', u'20171101': u'0', u'20171102': u'0', u'20171103': u'0', u'20171104': u'1', u'20171105': u'1', u'20171106': u'0', u'20171107': u'0', u'20161130': u'0', u'20170109': u'0', u'20170108': u'1', u'20170107': u'1', u'20170106': u'0', u'20170105': u'0', u'20170104': u'0', u'20170103': u'0', u'20170102': u'0', u'20170101': u'1', u'20170228': u'0', u'20170222': u'0', u'20170223': u'0', u'20170220': u'0', u'20170221': u'0', u'20170226': u'1', u'20170227': u'0', u'20170224': u'0', u'20170225': u'1', u'20170529': u'0', u'20161228': u'0', u'20171014': u'1', u'20171203': u'1', u'20170601': u'0', u'20170602': u'0', u'20170830': u'0', u'20170604': u'1', u'20170605': u'0', u'20170606': u'0', u'20170607': u'0', u'20170608': u'0', u'20170609': u'0', u'20171209': u'1', u'20171208': u'0', u'20170530': u'0', u'20170531': u'0', u'20171128': u'0', u'20171129': u'0', u'20171126': u'1', u'20171127': u'0', u'20171124': u'0', u'20171125': u'1', u'20171122': u'0', u'20171123': u'0', u'20171120': u'0', u'20171121': u'0', u'20170125': u'0', u'20170124': u'0', u'20170127': u'0', u'20170126': u'0', u'20170121': u'1', u'20170120': u'0', u'20170123': u'0', u'20170122': u'1', u'20170129': u'1', u'20170128': u'1', u'20170327': u'0', u'20170326': u'1', u'20170325': u'1', u'20170324': u'0', u'20170323': u'0', u'20170322': u'0', u'20170321': u'0', u'20170320': u'0', u'20170329': u'0', u'20170328': u'0', u'20170914': u'0', u'20170915': u'0', u'20170916': u'1', u'20170917': u'1', u'20170910': u'1', u'20170911': u'0', u'20170912': u'0', u'20170913': u'0', u'20170918': u'0', u'20170919': u'0', u'20170521': u'1', u'20170520': u'1', u'20170523': u'0', u'20170619': u'0', u'20171229': u'0', u'20171228': u'0', u'20170610': u'1', u'20171221': u'0', u'20170525': u'0', u'20171223': u'1', u'20171222': u'0', u'20171225': u'0', u'20171224': u'1', u'20171227': u'0', u'20170616': u'0', u'20170626': u'0', u'20170627': u'0', u'20170624': u'1', u'20170625': u'1', u'20170622': u'0', u'20170623': u'0', u'20170620': u'0', u'20170621': u'0', u'20161229': u'0', u'20161231': u'1', u'20170614': u'0', u'20170628': u'0', u'20170629': u'0', u'20170828': u'0', u'20170829': u'0', u'20171029': u'1', u'20171028': u'1', u'20161221': u'0', u'20171023': u'0', u'20171022': u'1', u'20171021': u'1', u'20171020': u'0', u'20171027': u'0', u'20170825': u'0', u'20171025': u'0', u'20171024': u'0', u'20161223': u'0', u'20171205': u'0', u'20170309': u'0', u'20170308': u'0', u'20170305': u'1', u'20170304': u'1', u'20170307': u'0', u'20170306': u'0', u'20170301': u'0', u'20170303': u'0', u'20170430': u'1', u'20171204': u'0', u'20170930': u'1', u'20161211': u'1', u'20170722': u'1', u'20161213': u'0', u'20171220': u'0', u'20161212': u'0', u'20170727': u'0', u'20170726': u'0', u'20170723': u'1', u'20161210': u'1', u'20170721': u'0', u'20170720': u'0', u'20161215': u'0', u'20161214': u'0', u'20161217': u'1', u'20161216': u'0', u'20161219': u'0', u'20161218': u'1', u'20170729': u'1', u'20170724': u'0', u'20171001': u'1', u'20171003': u'0', u'20171002': u'0', u'20171005': u'0', u'20171004': u'0', u'20171007': u'1', u'20170809': u'0', u'20171009': u'0', u'20170807': u'0', u'20170804': u'0', u'20170805': u'1', u'20170802': u'0', u'20170803': u'0', u'20170801': u'0', u'20170728': u'0', u'20170725': u'0', u'20170415': u'1', u'20170414': u'0', u'20170417': u'0', u'20170416': u'1', u'20170411': u'0', u'20170410': u'0', u'20170413': u'0', u'20170412': u'0', u'20170419': u'0', u'20170418': u'0', u'20170118': u'0', u'20170808': u'0', u'20171211': u'0', u'20170114': u'1', u'20170115': u'1', u'20170116': u'0', u'20170117': u'0', u'20170110': u'0', u'20170111': u'0', u'20170112': u'0', u'20170113': u'0', u'20170709': u'1', u'20170806': u'1', u'20171213': u'0', u'20171008': u'1', u'20170701': u'1', u'20170703': u'0', u'20170702': u'1', u'20170705': u'0', u'20170704': u'0', u'20170707': u'0', u'20170706': u'0', u'20170217': u'0', u'20170216': u'0', u'20170215': u'0', u'20170214': u'0', u'20170213': u'0', u'20170212': u'1', u'20170211': u'1', u'20170210': u'0', u'20170219': u'1', u'20170218': u'1', u'20171218': u'0', u'20170319': u'1', u'20171212': u'0', u'20170424': u'0', u'20170425': u'0', u'20170426': u'0', u'20171210': u'1', u'20170822': u'0', u'20170509': u'0', u'20170508': u'0', u'20171214': u'0', u'20171215': u'0', u'20171216': u'1', u'20171217': u'1', u'20170503': u'0', u'20170502': u'0', u'20170501': u'0', u'20170507': u'1', u'20170506': u'1', u'20170505': u'0', u'20170504': u'0', u'20171119': u'1', u'20171118': u'1', u'20170422': u'1', u'20171113': u'0', u'20171112': u'1', u'20171111': u'1', u'20170315': u'0', u'20171117': u'0', u'20171116': u'0', u'20171115': u'0', u'20171114': u'0', u'20170130': u'0', u'20170131': u'0', u'20170420': u'0', u'20171110': u'0', u'20170330': u'0', u'20170331': u'0', u'20171006': u'0', u'20170421': u'0', u'20170603': u'1', u'20170423': u'1', u'20161230': u'0', u'20171230': u'1', u'20170826': u'1', u'20170613': u'0', u'20170612': u'0', u'20170611': u'1', u'20170522': u'0', u'20170617': u'1', u'20170524': u'0', u'20170615': u'0', u'20170526': u'0', u'20161220': u'0', u'20170528': u'1', u'20161222': u'0', u'20170618': u'1', u'20161224': u'1', u'20161225': u'1', u'20161226': u'0', u'20161227': u'0', u'20171130': u'0', u'20171030': u'0', u'20171031': u'0', u'20170204': u'1', u'20170717': u'0', u'20170714': u'0', u'20170820': u'1', u'20170318': u'1', u'20170715': u'1', u'20170428': u'0', u'20170429': u'1', u'20170821': u'0', u'20170312': u'1', u'20170313': u'0', u'20170310': u'0', u'20170427': u'0', u'20170316': u'0', u'20170317': u'0', u'20170314': u'0', u'20170201': u'0', u'20170823': u'0', u'20170202': u'0', u'20170824': u'0', u'20170203': u'0', u'20171026': u'0', u'20170907': u'0', u'20170906': u'0', u'20170905': u'0', u'20170904': u'0', u'20170903': u'1', u'20170902': u'1', u'20170901': u'0', u'20170827': u'1', u'20170909': u'1', u'20170908': u'0'}


# def tran_info(info):
# 	year = info['year']
# 	month = info['month']
# 	start_day = info['start_day']
# 	end_day = info['end_day']
# 	if "half" in info.keys():
# 		if info['half'] == 0:
# 			half = info['half']
# 			return getMonth(year, month, start_day, end_day, half)
# 	return getMonth(year, month, start_day, end_day)


# def tran_info_add(info):
# 	year = info['year']
# 	month = info['month']
# 	start_day = info['start_day']
# 	end_day = info['end_day']
# 	if "half" in info.keys():
# 		if info['half'] == 0:
# 			half = info['half']
# 			return getMonthadd(year, month, start_day, end_day, half)
# 	return getMonthadd(year, month, start_day, end_day)


class ApplyView(View):

	def get(self, request):
		user = request.user
		leavetype = request.GET.get('leavetype')
		num = user.super.count()
		types = LeaveType.objects.all()
		start_date = str(datetime.datetime.now().date())
		return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date})

	def post(self,request):
		types = LeaveType.objects.all()
		user = request.user
		num = user.super.count()
		leavetype = request.POST.get('leavetype')
		apply_type = LeaveType.objects.get(name=leavetype)
		apply_file = request.FILES.get('apply_file')
		start_date = request.POST.get('start_date')
		apply_days = request.POST.get('apply_days')
		apply_info = request.POST.get('apply_info')
		apply_visitor = request.POST.get('apply_visitor')
		apply_address = request.POST.get('apply_address')
		chanjiatype = request.POST.get('chanjiatype')
		if apply_days:
			apply_days = float(apply_days)
		try:
			d1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
		except ValueError:
			return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '日期格式有误！'})
		
		now = datetime.datetime.now()
		# if (d1-now).days > 12:
		# 	return render(request, 'apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '最早允许提前12天申请。'})
		if (now-d1).days > now.day-1:
			return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '只允许补本个月的假。'})
		if leavetype == '加班':
			if api_res[d1.strftime('%Y%m%d')] == '0':
				return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '开始日期为正常工作日，不能申请加班。'})
		if leavetype == '年假':
			holiday_obj = UserHoliday.objects.get(user=user)
			if apply_days > holiday_obj.year_day:
				return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '年假剩余天数不足，不能申请。'})
		if leavetype == '调休':
			holiday_obj = UserHoliday.objects.get(user=user)
			if apply_days > holiday_obj.overtime_day:
				return render(request, 'leave-apply.html', {'user': user, 'num': num, 'types': types, "start_date": start_date, 'error': '调休剩余天数不足，不能申请。'})
		
		if leavetype == '外访':
			num = 0
			d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			while True:
				end_date = d2.strftime('%Y%m%d')
				if api_res[end_date] == '0':
					num = num+1
				if num >= apply_days:
					break
				d2 = d2 + datetime.timedelta(days=1)
			apply_desc = '客户：%s;  地点：%s;  备注：%s;'%(apply_visitor, apply_address, apply_info)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=apply_days, desc=apply_desc)
		elif leavetype == '产假':
			if chanjiatype == '1':
				apply_desc = '产假类型：产检假1天，备注：%s'%(apply_info)
				d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			elif chanjiatype == '15':
				apply_desc = '产假类型：产检假15天，备注：%s'%(apply_info)
				d2 = d1 + datetime.timedelta(days=14)
			else:
				apply_desc = '产假类型：产检假128天，备注：%s'%(apply_info)
				d2 = d1 + datetime.timedelta(days=127)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=int(chanjiatype), desc=apply_desc, upfile=apply_file)
		elif leavetype == '婚假':
			d2 = d1 + datetime.timedelta(days=9)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=10, desc=apply_info, upfile=apply_file)
		elif leavetype == '病假':
			num = 0
			d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			while True:
				end_date = d2.strftime('%Y%m%d')
				if api_res[end_date] == '0':
					num = num+1
				if num >= apply_days:
					break
				d2 = d2 + datetime.timedelta(days=1)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=apply_days, desc=apply_info, upfile=apply_file)
		elif leavetype == '加班':
			num = 0
			d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			while True:
				end_date = d2.strftime('%Y%m%d')
				if api_res[end_date] == '1':
					num = num+1
				if num >= apply_days:
					break
				d2 = d2 + datetime.timedelta(days=1)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=apply_days, desc=apply_info)
		else:
			num = 0
			d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			while True:
				end_date = d2.strftime('%Y%m%d')
				if api_res[end_date] == '0':
					num = num+1
				if num >= apply_days:
					break
				d2 = d2 + datetime.timedelta(days=1)
			Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=apply_type, total_day=apply_days, desc=apply_info)
			
		email = request.user.pro.superior.email
		if not email:
			return render(request, 'leave-apply.html', {'user': user, 'error': '上级邮箱不存在'
				, 'start_date': start_date, 'num': num, 'types': types, 'leavetype': leavetype})
		email_list = [email]
		content = """
				<p>您好，%s提交了一份请假申请，请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>审批。</p>
				"""%(request.user.first_name)
		send_mail(email_list, 'CAS系统假期申请', content)
		return HttpResponseRedirect('/leave/notes/')


@login_required
def awayapply(request):
	obj_id = int(request.GET.get('obj_id'))
	obj = Apply.objects.get(id=obj_id)
	obj.status = True
	obj.result = 2
	obj.save()
	email = obj.user.pro.superior.email
	content = '%s 申请的假期已取消，望周知！'%obj.user.first_name
	send_mail([email, obj.user.email], 'CAS系统假期申请', content)
	return HttpResponseRedirect('/leave/notes/')


@login_required
def notes(request):
	user = request.user
	num = user.super.count()
	apply_date = str(datetime.datetime.now().date())[:7] + '-01'
	applyed_objs = Apply.objects.filter(user=user, status=True)
	applying_objs = Apply.objects.filter(user=user, status=False)
	page_num = request.GET.get('page')
	if page_num:
		page_num = int(page_num)
	p = Paginator(applyed_objs, 14)
	try:
		page = p.page(int(page_num))
	except:
		page = p.page(1)
	return render(request, 'leave-notes.html', {'user': user, 'applyed_objs': applyed_objs, 'applying_objs': applying_objs\
		, 'num': num, 'page':page})


@login_required
def notesearch(request):
	user = request.user
	num = user.super.count()
	year_month = request.POST.get('search')
	try:
		year = int(year_month.split('-')[0])
		month = int(year_month.split('-')[1])
		objs = Apply.objects.filter(user=user, apply_date__year=year, apply_date__month=month)
	except Exception, e:
		errlog.error('查询记录错误:'+traceback.format_exc())
		return HttpResponseRedirect('/leave/notes/')
	return render(request, 'leave-notes.html', {'user': user, 'objs': objs, 'num': num})


@login_required
def myholiday(request):
	user = request.user
	num = user.super.count()
	obj = UserHoliday.objects.get(user=user)
	year = datetime.datetime.now().year
	month = datetime.datetime.now().month
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)
	try:
		monthapply_obj = MonthApply.objects.get(user=user, year_month=year_month)
	except MonthApply.DoesNotExist:
		MonthApply.objects.create(user=user, year_month=year_month)
		monthapply_obj = MonthApply.objects.get(user=user, year_month=year_month)

	user_list = User.objects.filter(pro__superior=user)
	objs = []
	for u in user_list:
		holiday_objs = UserHoliday.objects.get(user=u)
		try:
			monthapply_objs = MonthApply.objects.get(user=u, year_month=year_month)
		except:
			MonthApply.objects.create(user=u, year_month=year_month)
			monthapply_objs = MonthApply.objects.get(user=u, year_month=year_month)
		objs.append((holiday_objs, monthapply_objs))
	return render(request, 'leave-myholiday.html', {'user': user, 'obj': obj, 'num': num, 'monthapply_obj': monthapply_obj\
		, 'objs': objs})


@login_required
def myapproval(request):
	user = request.user
	num = user.super.count()
	user_list = User.objects.filter(pro__superior=user)
	year = datetime.datetime.now().year
	month = datetime.datetime.now().month
	applyed_objs = Apply.objects.filter(user__in=user_list, status=True)
	applying_objs = Apply.objects.filter(user__in=user_list, status=False)	
	page_num = request.GET.get('page')
	if page_num:
		page_num = int(page_num)
	p = Paginator(applyed_objs, 14)
	try:
		page = p.page(int(page_num))
	except:
		page = p.page(1)
	return render(request, 'leave-myapproval.html', {'user': user, 'applying_objs': applying_objs, 'num': num\
		, 'applyed_objs': applyed_objs, 'page': page})


@login_required
def result(request):
	obj_id = request.GET.get('obj_id')
	res = request.GET.get('res')
	apply_obj = Apply.objects.get(pk=obj_id)
	user = apply_obj.user
	email = apply_obj.user.email
	leavetype = apply_obj.leavetype.name
	month = datetime.datetime.now().month
	next_month = month + 1
	year = datetime.datetime.now().year
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)
	if next_month < 10:
		next_year_month = str(year) + '0' + str(next_month)
	else:
		next_year_month = str(year) + str(next_month)
	if res == '0':
		apply_obj.result = 0
		content = """<p>你的申请被拒绝。<p>"""	
		mail_list = [email]	
	else:
		apply_obj.result = 1
		start_date = datetime.datetime.strftime(apply_obj.start_date,'%Y%m%d')
		d1 = datetime.datetime.strptime(start_date, "%Y%m%d")
		end_date = datetime.datetime.strftime(apply_obj.end_date,'%Y%m%d')
		holiday_obj = UserHoliday.objects.get(user=user)
		now_monthapply_obj = MonthApply.objects.get(user=user, year_month=year_month)
		if start_date[4:6] != end_date[4:6]:
			month_total_days = calendar.monthrange(int(start_date[:4]),int(start_date[4:6]))[1]
			middle_date = start_date[:6] + str(month_total_days)
			######找出本月的最后一个工作日日期##########
			while True:
				if api_res[middle_date] == '0':
					break
				month_total_days = month_total_days - 1
				middle_date = start_date[:6] + str(month_total_days)
			d2 = datetime.datetime.strptime(middle_date, "%Y%m%d")
			now_month_days = (d2-d1).days + 1
			next_month_days = apply_obj.total_day - now_month_days
			if str(next_month_days)[-1] == '5':
				now_month_days = now_month_days - 0.5
				next_month_days = next_month_days + 0.5
			try:
				next_monthapply_obj = MonthApply.objects.get(user=user, year_month=end_date[:4]+end_date[5:7])
			except MonthApply.DoesNotExist:
				MonthApply.objects.create(user=user, year_month=end_date[:4]+end_date[5:7])
				next_monthapply_obj = MonthApply.objects.get(user=user, year_month=end_date[:4]+end_date[5:7])
			if leavetype == '加班':
				now_monthapply_obj.add_day = now_monthapply_obj.add_day + now_month_days
				next_monthapply_obj.add_day = next_monthapply_obj.add_day + next_month_days
				now_monthapply_obj.save()
				next_monthapply_obj.save()
				holiday_obj.overtime_day = holiday_obj.overtime_day + apply_obj.total_day
				holiday_obj.save()
			elif leavetype == '产假' and apply_obj.total_day == 128:
				pass
			else:
				if leavetype == '调休':
					holiday_obj.overtime_day = holiday_obj.overtime_day - apply_obj.total_day
					holiday_obj.save()
				elif leavetype == '年假':
					holiday_obj.year_day = holiday_obj.year_day - apply_obj.total_day
					holiday_obj.save()
				now_monthapply_obj.apply_day = now_monthapply_obj.apply_day + now_month_days
				next_monthapply_obj.apply_day = next_monthapply_obj.apply_day + next_month_days
				now_monthapply_obj.save()
				next_monthapply_obj.save()
		else:
			try:
				monthapply_obj =  MonthApply.objects.get(user=user, year_month=start_date[:6])
			except MonthApply.DoesNotExist:
				monthapply_obj =  MonthApply.objects.create(user=user, year_month=start_date[:6])
				monthapply_obj =  MonthApply.objects.get(user=user, year_month=start_date[:6])
			if leavetype == '加班':
				holiday_obj.overtime_day = holiday_obj.overtime_day + apply_obj.total_day
				holiday_obj.save()
				monthapply_obj.add_day = monthapply_obj.add_day + apply_obj.total_day
				monthapply_obj.save()
			elif leavetype == '产假' and apply_obj.total_day == 128:
				pass
			else:
				if leavetype == '调休':
					holiday_obj.overtime_day = holiday_obj.overtime_day - apply_obj.total_day
					holiday_obj.save()
				elif leavetype == '年假':
					holiday_obj.year_day = holiday_obj.year_day - apply_obj.total_day
					holiday_obj.save()
				monthapply_obj.apply_day = monthapply_obj.apply_day + apply_obj.total_day
				monthapply_obj.save()
		content = """
				<p>%s提交的%s申请已通过审批，详情请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>查看。</p>
				"""%(apply_obj.user.first_name, leavetype)
		mail_list = [email,'xueli.cai@100credit.com']        #添加hr邮箱
	send_mail(mail_list, 'CAS系统假期申请', content)
	apply_obj.status = True
	apply_obj.save()
	return HttpResponseRedirect("/leave/myapproval/")


@login_required
def manager(request):
	user = request.user
	num = user.super.count()
	month = datetime.datetime.now().month
	year = datetime.datetime.now().year
	if month < 10:
		year_month = str(year) + '0' + str(month)
	else:
		year_month = str(year) + str(month)
	month_objs = MonthApply.objects.filter(year_month=year_month, apply_day__gte=0).exclude(apply_day=0)
	applying_objs = Apply.objects.filter(status=False)
	return render(request, 'leave-manager1.html', {'user': user, 'num': num, 'month_objs': month_objs})


class ApprovaledList(ListView):

	queryset = Apply.objects.filter(status=True,result=1)
	template_name = 'leave-manager2.html'

	def get_context_data(self, **kwargs):
		context = super(ApprovaledList, self).get_context_data(**kwargs)
		user = self.request.user
		num = user.super.count()
		page_num = self.request.GET.get('page')
		if page_num:
			page_num = int(page_num)
		objs = Apply.objects.filter(status=True,result=1)
		p = Paginator(objs, 15)
		try:
			page = p.page(int(page_num))
		except:
			page = p.page(1)
		context['page'] = page
		context['num'] = num
		context['user'] = user
		return context


class ApprovalingList(ListView):

	queryset = Apply.objects.filter(status=False)
	template_name = 'leave-manager3.html'

	def get_context_data(self, **kwargs):
		context = super(ApprovalingList, self).get_context_data(**kwargs)
		user = self.request.user
		num = user.super.count()
		page_num = self.request.GET.get('page')
		if page_num:
			page_num = int(page_num)
		objs = Apply.objects.filter(status=False)
		p = Paginator(objs, 15)
		try:
			page = p.page(int(page_num))
		except:
			page = p.page(1)
		context['page'] = page
		context['num'] = num
		context['user'] = user
		return context


@login_required
def managersearch2(request):
	user = request.user
	num = user.super.count()
	name = request.POST.get('search')
	try:
		user_list = User.objects.filter(first_name__contains=name)
		page = Apply.objects.filter(user__in=user_list,status=True,result=1)
	except Exception:
		errlog.error('查询错误:'+traceback.format_exc())
		return HttpResponseRedirect('/leave/manager2/')
	return render(request, 'leave-manager2.html', {'user': user, 'page': page, 'num': num})


@login_required
def managersearch3(request):
	user = request.user
	num = user.super.count()
	name = request.POST.get('search')
	try:
		user_list = User.objects.filter(first_name__contains=name)
		page = Apply.objects.filter(user__in=user_list,status=False)
	except Exception:
		errlog.error('查询错误:'+traceback.format_exc())
		return HttpResponseRedirect('/leave/manager3/')
	return render(request, 'leave-manager3.html', {'user': user, 'page': page, 'num': num})


@login_required
def down(request):
	obj_id = request.GET.get('obj_id')
	obj = Apply.objects.get(id=obj_id)
	fn = obj.upfile.path

	filename = str(os.path.split(fn)[1])
	_, end = os.path.splitext(filename)
	now = time.strftime('%Y%m%d',time.localtime())
	
	def readFile(fn, buf_size=262144):
		f = open(fn, "rb")
		while True:
			c = f.read(buf_size)
			if c:
				yield c
			else:
				break
		f.close()

	response = StreamingHttpResponse(readFile(fn),content_type='application/octet-stream') 
	response['Content-Disposition'] = 'attachment; filename={0}'.format(now+end)
	return response


@login_required
def write_excel(request):
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="monthnotes.xls"'

	month = datetime.datetime.now().month
	year = datetime.datetime.now().year
	# objs = Apply.objects.filter(apply_date__gte=datetime.date(year, month, 1),result=1)
	
	writer = csv.writer(response)
	month = datetime.datetime.now().month
	year = datetime.datetime.now().year
	d = calendar.monthrange(year, month)
	if month < 10:
		year_month = str(year) + '0' + str(month)
		apply_start_date = str(year) + '-0' + str(month) + '-01'
		apply_end_date = str(year) + '-0' + str(month) + '-' + str(d[1])
	else:
		year_month = str(year) + str(month)
		apply_start_date = str(year) + '-' + str(month) + '-' + '01'
		apply_end_date = str(year) + '-' + str(month) + '-' + str(d[1])

	write_list = []
	users = User.objects.all()
	for user in users:
		udict = {'员工编号': user.pro.num_id, '申请人': user.first_name, '外访': 0, '出差': 0, '调休': 0, '年假': 0\
		, '事假': 0, '婚假': 0, '产假': 0, '病假': 0, '丧假': 0, '其他': 0, '加班': 0}
		try:
			month_obj = MonthApply.objects.get(user=user, year_month=year_month)
		except:
			errlog.error('导出文件错误，该申请人不存在月申请记录：'+user.first_name+traceback.format_exc())
			continue
		udict.update({'month_apply': month_obj.apply_day})
		applys= Apply.objects.filter(user=user, start_date__month=month, result=1)
		if month == 1:
			applys_pre = Apply.objects.filter(user=user, end_date__month=month, start_date__month=12, result=1)
		else:
			applys_pre = Apply.objects.filter(user=user, end_date__month=month, start_date__month=month-1, result=1)

		for obj in applys_pre:
			start_date = datetime.datetime.strftime(obj.start_date,'%Y%m%d')
			d1 = datetime.datetime.strptime(start_date, "%Y%m%d")
			end_date = datetime.datetime.strftime(obj.end_date,'%Y%m%d')
			holiday_obj = UserHoliday.objects.get(user=user)
			now_monthapply_obj = MonthApply.objects.get(user=user, year_month=year_month)
			month_total_days = calendar.monthrange(int(start_date[:4]),int(start_date[4:6]))[1]
			middle_date = start_date[:6] + str(month_total_days)
			######找出上个月的最后一个工作日日期##########
			while True:
				if obj.leavetype.name == '加班':
					if api_res[middle_date] == '1':
						break
				else:
					if api_res[middle_date] == '0':
						break
				month_total_days = month_total_days - 1
				middle_date = start_date[:6] + str(month_total_days)
			d2 = datetime.datetime.strptime(middle_date, "%Y%m%d")
			now_month_days = (d2-d1).days + 1
			next_month_days = obj.total_day - now_month_days
			if str(next_month_days)[-1] == '5':
				now_month_days = now_month_days - 0.5
				next_month_days = next_month_days + 0.5
			udict[obj.leavetype.name] = udict[obj.leavetype.name] + next_month_days

		for obj in applys:
			start_date = datetime.datetime.strftime(obj.start_date,'%Y%m%d')
			d1 = datetime.datetime.strptime(start_date, "%Y%m%d")
			end_date = datetime.datetime.strftime(obj.end_date,'%Y%m%d')
			holiday_obj = UserHoliday.objects.get(user=user)
			now_monthapply_obj = MonthApply.objects.get(user=user, year_month=year_month)
			if start_date[4:6] != end_date[4:6]:
				month_total_days = calendar.monthrange(int(start_date[:4]),int(start_date[4:6]))[1]
				middle_date = start_date[:6] + str(month_total_days)
				######找出本月的最后一个工作日日期##########
				while True:
					if obj.leavetype.name == '加班':
						if api_res[middle_date] == '1':
							break
					else:
						if api_res[middle_date] == '0':
							break
					month_total_days = month_total_days - 1
					middle_date = start_date[:6] + str(month_total_days)
				d2 = datetime.datetime.strptime(middle_date, "%Y%m%d")
				now_month_days = (d2-d1).days + 1
				next_month_days = obj.total_day - now_month_days
				if str(next_month_days)[-1] == '5':
					now_month_days = now_month_days - 0.5
					next_month_days = next_month_days + 0.5
				udict[obj.leavetype.name] = udict[obj.leavetype.name] + now_month_days
			else:
				udict[obj.leavetype.name] = udict[obj.leavetype.name] + obj.total_day
		write_list.append(udict)

	wb = Workbook(encoding='utf-8')  
	sheet1 = wb.add_sheet(u"本月记录,加班和产假128天不计入本月申请")  
	sheet1.write(0, 0, u"员工编号")  
	sheet1.write(0, 1, u"申请人")  
	sheet1.write(0, 2, u"外访")  
	sheet1.write(0, 3, u"出差")
	sheet1.write(0, 4, u"调休")  
	sheet1.write(0, 5, u"年假")  
	sheet1.write(0, 6, u"事假")  
	sheet1.write(0, 7, u"婚假")  
	sheet1.write(0, 8, u"产假")  
	sheet1.write(0, 9, u"病假")  
	sheet1.write(0, 10, u"丧假")  
	sheet1.write(0, 11, u"其他")  
	sheet1.write(0, 12, u"加班")
	sheet1.write(0, 13, u"本月申请总天数")
	sheet1_row = 1  
	for obj in write_list:
		sheet1.write(sheet1_row, 0, obj['员工编号'])  
		sheet1.write(sheet1_row, 1, obj['申请人'])  
		sheet1.write(sheet1_row, 2, obj['外访'])
		sheet1.write(sheet1_row, 3, obj['出差'])
		sheet1.write(sheet1_row, 4, obj['调休'])
		sheet1.write(sheet1_row, 5, obj['年假'])
		sheet1.write(sheet1_row, 6, obj['事假'])
		sheet1.write(sheet1_row, 7, obj['婚假'])
		sheet1.write(sheet1_row, 8, obj['产假'])
		sheet1.write(sheet1_row, 9, obj['病假'])
		sheet1.write(sheet1_row, 10, obj['丧假'])
		sheet1.write(sheet1_row, 11, obj['其他'])
		sheet1.write(sheet1_row, 12, obj['加班'])
		sheet1.write(sheet1_row, 13, obj['month_apply'])
		sheet1_row += 1
	io = StringIO.StringIO()
	wb.save(io)  
	io.seek(0)
	response.write(io.getvalue()) 
	return response



