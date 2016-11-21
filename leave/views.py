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
from cas.models import Pro
from xlwt import * 

import StringIO
import logging
import datetime
import traceback
import calendar
import csv
import smtplib
import codecs
import re
import os

# Create your views here.


errlog = logging.getLogger('daserr')
leap = {1:31, 2:29, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
nleap = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}


def tran_info(info):
	year = info['year']
	month = info['month']
	start_day = info['start_day']
	end_day = info['end_day']
	if "half" in info.keys():
		if info['half'] == 0:
			half = info['half']
			return getMonth(year, month, start_day, end_day, half)
	return getMonth(year, month, start_day, end_day)


def tran_info_add(info):
	year = info['year']
	month = info['month']
	start_day = info['start_day']
	end_day = info['end_day']
	if "half" in info.keys():
		if info['half'] == 0:
			half = info['half']
			return getMonthadd(year, month, start_day, end_day, half)
	return getMonthadd(year, month, start_day, end_day)


class ApplyView(View):

	def get(self, request):
		user = request.user
		leavetype = request.GET.get('leavetype')
		num = user.super.count()
		applytype = LeaveType.objects.all()
		start_date = str(datetime.datetime.now().date())
		if leavetype == '外访':
			form = VisitForm()
		elif leavetype == '产假':
			form = MaterForm()
		elif leavetype in ['婚假', '病假']:
			form = FileForm()
		else:
			form = ApplyForm()
		if leavetype in ['产假', '婚假']:
			return render(request, 'apply1.html', {'user': user, 'form': form, 'num': num, 'types': applytype, 'leavetype': leavetype, "start_date": start_date})
		if leavetype in ['病假', '事假', '其他', '加班', '调休', '年假', '出差', '外访', '丧假']:
			return render(request, 'apply2.html', {'user': user, 'form': form, 'num': num, 'types': applytype, 'leavetype': leavetype, "start_date": start_date})
		return render(request, 'apply.html', {'user': user, 'form': form, 'num': num, 'types': applytype, "start_date": start_date})

	def post(self,request):
		applytype = LeaveType.objects.all()
		user = request.user
		num = user.super.count()
		leavetype = request.POST.get('leavetype')
		type_obj = LeaveType.objects.get(name=leavetype)
		upfile = request.FILES.get('upfile')


		if leavetype == '外访':
			form = VisitForm(request.POST)
		elif leavetype == '产假':
			form = MaterForm(request.POST)
		elif leavetype in ['婚假', '病假']:
			form = FileForm(request.POST)
		else:
			form = ApplyForm(request.POST)
		email = request.user.pro.superior.email
		email_list = [email]
		if form.is_valid():
			start_date = request.POST.get('startdate')
			desc = form.cleaned_data['desc']
			d1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
			if leavetype == '婚假':
				d2 = d1 + datetime.timedelta(days=10)
				if upfile:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=type_obj, total_day=10, desc=desc, upfile=upfile)
				else:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=type_obj, total_day=10, desc=desc)
				if not email:
					error = '上级邮箱不存在'
					return render(request, 'apply1.html', {'user': user, 'form': form, 'error': error
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				content = """
						<p>申请人：%s</p>
						<p>请假类型：%s</p>
						<p>请假时间：%s　- %s</p>
						<p>请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>审批</p>
						"""%(request.user.first_name, leavetype, str(d1.date()), str(d2.date()))
				try:
					send_mail(email_list, 'CAS系统假期申请', content)
				except smtplib.SMTPRecipientsRefused:
					return render(request, "apply1.html", {'error': '该邮箱不存在', 'form': form
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				except Exception:
					errlog.error('请假邮件发送失败：' + traceback.format_exc())
					return render(request, "apply1.html", {'error': '未知错误请联系管理员', 'form': form
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
			elif leavetype == '产假':
				matertype = int(form.cleaned_data['matertype'])
				desc = form.cleaned_data['desc']
				if matertype == 1:
					info = '产假类型：产检假1天，备注：%s'%(desc)
				elif matertype == 15:
					info = '产假类型：陪产假15天，备注：%s'%(desc)
				else:
					info = '产假类型：产假128天，备注：%s'%(desc)
				d2 = d1 + datetime.timedelta(days=matertype)
				if upfile:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=type_obj, total_day=matertype, desc=info, upfile=upfile)
				else:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
							, leavetype=type_obj, total_day=matertype, desc=info)
				if not email:
					error = '上级邮箱不存在'
					return render(request, 'apply1.html', {'user': user, 'form': form, 'error': error
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				content = """
						<p>申请人：%s</p>
						<p>请假类型：%s</p>
						<p>请假时间：%s　- %s</p>
						<p>请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>审批</p>
						"""%(request.user.first_name, leavetype, str(d1.date()), str(d2.date()))
				try:
					send_mail(email_list, 'CAS系统假期申请', content)
				except smtplib.SMTPRecipientsRefused:
					return render(request, "apply1.html", {'error': '该邮箱不存在', 'form': form
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				except Exception:
					errlog.error('请假邮件发送失败：' + traceback.format_exc())
					return render(request, "apply1.html", {'error': '未知错误请联系管理员', 'form': form
						, 'start_date': start_date, 'num': num, 'types': applytype, 'leavetype': leavetype})

			elif leavetype == '外访':
				end_date = request.POST.get('enddate')
				if not end_date:
					return render(request, 'apply2.html',{'user': user, 'form': form, 'error': '结束日期不能为空'\
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype}) 
				half = request.POST.get('half')
				# desc = request.POST.get('desc')

				visitor = request.POST.get('visitor')
				address = request.POST.get('address')
				note = request.POST.get('note')
				desc = '客户：%s;  地点：%s;  备注：%s;'%(visitor, address, note)
				d2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
				total_day = (d2-d1).days
				if total_day < 0:
					return render(request, 'apply2.html', {'user': user, 'form': form, 'error': '结束日期不能小于开始日期'\
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				Apply.objects.create(user=user, start_date=d1, end_date=d2
						, leavetype=type_obj, desc=desc, half=int(half))
				if not email:
					error = '上级邮箱不存在'
					return render(request, 'apply2.html', {'user': user, 'form': form, 'error': error
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				content = """
						<p>申请人：%s</p>
						<p>请假类型：%s</p>
						<p>请假时间：%s　- %s</p>
						<p>请假理由：%s</p>
						<p>请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>审批</p>
						"""%(request.user.first_name, leavetype, str(d1.date()), str(d2.date()), desc)
				try:
					send_mail(email_list, 'CAS系统假期申请', content)
				except smtplib.SMTPRecipientsRefused:
					return render(request, "apply2.html", {'error': '该邮箱不存在', 'form': form
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				except Exception:
					errlog.error('请假邮件发送失败：' + traceback.format_exc())
					return render(request, "apply2.html", {'error': '未知错误请联系管理员', 'form': form
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})

			else:
				end_date = request.POST.get('enddate')
				if not end_date:
					return render(request, 'apply2.html',{'user': user, 'form': form, 'error': '结束日期不能为空'\
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype}) 
				half = request.POST.get('half')
				desc = request.POST.get('desc')
				d2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
				total_day = (d2-d1).days
				if total_day < 0:
					return render(request, 'apply2.html', {'user': user, 'form': form, 'error': '结束日期不能小于开始日期'\
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				if upfile:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
							, leavetype=type_obj, desc=desc, half=int(half), upfile=upfile)
				else:
					Apply.objects.create(user=user, start_date=d1, end_date=d2
							, leavetype=type_obj, desc=desc, half=int(half))
				if not email:
					error = '上级邮箱不存在'
					return render(request, 'apply2.html', {'user': user, 'form': form, 'error': error
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				content = """
						<p>申请人：%s</p>
						<p>请假类型：%s</p>
						<p>请假时间：%s　- %s</p>
						<p>请假理由：%s</p>
						<p>请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>审批</p>
						"""%(request.user.first_name, leavetype, str(d1.date()), str(d2.date()), desc)
				try:
					send_mail(email_list, 'CAS系统假期申请', content)
				except smtplib.SMTPRecipientsRefused:
					return render(request, "apply2.html", {'error': '该邮箱不存在', 'form': form
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
				except Exception:
					errlog.error('请假邮件发送失败：' + traceback.format_exc())
					return render(request, "apply2.html", {'error': '未知错误请联系管理员', 'form': form
						, 'start_date': start_date, 'end_date': end_date, 'num': num, 'types': applytype, 'leavetype': leavetype})
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
	objs = Apply.objects.filter(user=user, apply_date__gte=apply_date)
	return render(request, 'notes.html', {'user': user, 'objs': objs, 'num': num})


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
	return render(request, 'notes.html', {'user': user, 'objs': objs, 'num': num})


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
	return render(request, 'myholiday.html', {'user': user, 'obj': obj, 'num': num, 'monthapply_obj': monthapply_obj\
		, 'objs': objs})


@login_required
def myapproval(request):
	err = request.GET.get('err')
	user = request.user
	num = user.super.count()

	user_list = User.objects.filter(pro__superior=user)
	year = datetime.datetime.now().year
	month = datetime.datetime.now().month
	objs = Apply.objects.filter(user__in=user_list, apply_date__year=year, apply_date__month=month)	

	if err:
		return render(request, 'myapproval.html', {'user': user, 'objs': objs, 'num': num, 'error': err})

	return render(request, 'myapproval.html', {'user': user, 'objs': objs, 'num': num})


@login_required
def result(request):
	obj_id = request.GET.get('obj_id')
	res = request.GET.get('res')
	apply_obj = Apply.objects.get(pk=obj_id)
	user = apply_obj.user
	email = apply_obj.user.email
	if res == '0':
		apply_obj.result = 0
		content = """<p>你的申请被拒绝。<p>"""	
		mail_list = [email]	
	else:
		apply_obj.result = 1
		half = apply_obj.half
		start_date = str(apply_obj.start_date)
		end_date = str(apply_obj.end_date)
		d1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
		d2 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
		leavetype = apply_obj.leavetype.name
		if leavetype in ['产假', '婚假']:
			pass
		elif leavetype in ['病假', '事假', '其他', '调休', '年假', '出差', '外访', '丧假']:
			start_year = d1.year
			start_month = d1.month
			start_day = d1.day
			end_year = d2.year
			end_month = d2.month
			end_day = d2.day
			info_list = []
			if start_year == end_year:
				if calendar.isleap(start_year):
					cal = leap
				else:
					cal = nleap
				if start_month == end_month:
					info1 = {
							"year": start_year,
							"month": start_month,
							"start_day": start_day,
							"end_day": end_day,
							"half": half
						}
					info_list.append(info1)
				else:
					info1 = {
						"year": start_year,
						"month": start_month,
						"start_day": start_day,
						"end_day": cal[start_month],
						"half": half
					}
					info_list.append(info1)
					for mon in range(start_month+1, end_month):
						info = {
							"year": start_year,
							"month": mon,
							"start_day": 1,
							"end_day": cal[mon]
						}
						info_list.append(info)
					info2 = {
						"year":start_year,
						"month": end_month,
						"start_day": 1,
						"end_day": end_day,
					}
					info_list.append(info2)
			else:
				if calendar.isleap(start_year):
					start_cal = leap
				else:
					start_cal = nleap
				if calendar.isleap(end_year):
					end_cal = leap
				else:
					end_cal = nleap
				info1 = {
					"year": start_year,
					"month": start_month,
					"start_day": start_day,
					"end_day": start_cal[start_month],
					"half": half
					}
				info_list.append(info1)
				info2 = {
					"year": end_year,
					"month": end_month,
					"start_day": 1,
					"end_day": end_day
					}
				for mon1 in range(start_month+1, 13):
					info = {
						"year": start_year,
						"month": mon1,
						"start_day": 1,
						"end_day": start_cal[mon1]
					}
					info_list.append(info)
				for mon2 in range(1, end_month):
					info = {
						"year": end_year,
						"month": mon2,
						"start_day": 1,
						"end_day": edn_cal[mon2]
					}
					info_list.append(info)
				info_list.append(info2)
			results = map(tran_info, info_list)
			holiday_obj = UserHoliday.objects.get(user=user)
			apply_total_day = 0
			for res in results:
				if res['month_apply_day'] <= 0:
					return HttpResponseRedirect("/leave/myapproval/?err=%s"%('申请时间区间有误，无法通过审批，请拒绝！'))
				apply_total_day = apply_total_day + res['month_apply_day']

			if leavetype == '调休':
				if holiday_obj.overtime_day < apply_total_day:
					return HttpResponseRedirect("/leave/myapproval/?err=%s"%('调休剩余天数不够，无法通过审批，请拒绝！'))
				holiday_obj.overtime_day = holiday_obj.overtime_day - apply_total_day
				
			elif leavetype == '年假':
				if holiday_obj.year_day < apply_total_day:
					return HttpResponseRedirect("/leave/myapproval/?err=%s"%('年假剩余天数不够，无法通过审批，请拒绝！'))
				holiday_obj.year_day = holiday_obj.year_day - apply_total_day

			elif leavetype == '丧假':
				if apply_total_day > 3:
					return HttpResponseRedirect("/leave/myapproval/?err=%s"%('丧假最多申请三天，无法通过审批，请拒绝！'))
			for res in results:
				try:
					monthapply_obj = MonthApply.objects.get(user=user, year_month=res['year_month'])
				except MonthApply.DoesNotExist:
					monthapply_obj = MonthApply.objects.create(user=user, year_month=res['year_month'])
				monthapply_obj.apply_day = monthapply_obj.apply_day + res['month_apply_day']
				monthapply_obj.save()
			holiday_obj.save()
			apply_obj.total_day = apply_total_day
			apply_obj.save()
		else:
			start_year = d1.year
			start_month = d1.month
			start_day = d1.day
			end_year = d2.year
			end_month = d2.month
			end_day = d2.day
			info_list = []
			if start_year == end_year:
				if calendar.isleap(start_year):
					cal = leap
				else:
					cal = nleap
				if start_month == end_month:
					info1 = {
							"year": start_year,
							"month": start_month,
							"start_day": start_day,
							"end_day": end_day,
							"half": half
						}
					info_list.append(info1)
				else:
					info1 = {
						"year": start_year,
						"month": start_month,
						"start_day": start_day,
						"end_day": cal[start_month],
						"half": half
					}
					info_list.append(info1)
					for mon in range(start_month+1, end_month):
						info = {
							"year": start_year,
							"month": mon,
							"start_day": 1,
							"end_day": cal[mon]
						}
						info_list.append(info)
					info2 = {
						"year":start_year,
						"month": end_month,
						"start_day": 1,
						"end_day": end_day,
					}
					info_list.append(info2)
			else:
				if calendar.isleap(start_year):
					start_cal = leap
				else:
					start_cal = nleap
				if calendar.isleap(end_year):
					end_cal = leap
				else:
					end_cal = nleap
				info1 = {
					"year": start_year,
					"month": start_month,
					"start_day": start_day,
					"end_day": start_cal[start_month],
					"half": half
					}
				info_list.append(info1)
				info2 = {
					"year": end_year,
					"month": end_month,
					"start_day": 1,
					"end_day": end_day
					}
				for mon1 in range(start_month+1, 13):
					info = {
						"year": start_year,
						"month": mon1,
						"start_day": 1,
						"end_day": start_cal[mon1]
					}
					info_list.append(info)
				for mon2 in range(1, end_month):
					info = {
						"year": end_year,
						"month": mon2,
						"start_day": 1,
						"end_day": edn_cal[mon2]
					}
					info_list.append(info)
				info_list.append(info2)
			results = map(tran_info_add, info_list)
			holiday_obj = UserHoliday.objects.get(user=user)
			apply_total_day = 0
			for res in results:
				if res['month_add_day'] <= 0:
					return HttpResponseRedirect("/leave/myapproval/?err=%s"%('申请时间区间有误，无法通过审批，请拒绝！'))
			for res in results:
				try:
					monthapply_obj = MonthApply.objects.get(user=user, year_month=res['year_month'])
				except MonthApply.DoesNotExist:
					monthapply_obj = MonthApply.objects.create(user=user, year_month=res['year_month'])
				monthapply_obj.add_day = monthapply_obj.add_day + res['month_add_day']
				monthapply_obj.save()
				apply_total_day = apply_total_day + res['month_add_day']
			holiday_obj.overtime_day = holiday_obj.overtime_day + apply_total_day
			holiday_obj.save()
			apply_obj.total_day = apply_total_day
			apply_obj.save()
		content = """
				<p>%s提交的%s申请已通过审批，详情请登陆<a href="http://cas.100credit.cn/leave/myapproval/">CAS系统</a>查看。</p>
				"""%(apply_obj.user.first_name, leavetype)
		mail_list = [email,'lei.xu@100credit.com']        #添加hr邮箱
	try:
		send_mail(mail_list, 'CAS系统假期申请', content)
	except smtplib.SMTPRecipientsRefused:
		content = user.first_name +',' + email + ',申请人邮箱有误，请告知修改.'
		send_mail(['cas@100credit.com'], 'CAS系统假期申请,申请人邮箱错误', content)
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
	applyd_objs = Apply.objects.filter(apply_date__year=year,apply_date__month=month,status=True,result=1) 
	applying_objs = Apply.objects.filter(apply_date__year=year,apply_date__month=month,status=False)
	return render(request, 'vacation_manager.html', {'user': user, 'applyd_objs': applyd_objs, 'applying_objs': applying_objs, 'num': num, 'month_objs': month_objs})


@login_required
def down(request):
	obj_id = request.GET.get('obj_id')
	obj = Apply.objects.get(id=obj_id)
	fn = obj.upfile.path
	filename = os.path.split(fn)[1]
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
	response['Content-Disposition'] = 'attachment; filename=%s' %filename
	return response


@login_required
def write_excel(request):
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="monthnotes.xls"'

	month = datetime.datetime.now().month
	year = datetime.datetime.now().year
	objs = Apply.objects.filter(apply_date__gte=datetime.date(year, month, 1),result=1)
	
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
		udict = {'id_num': user.pro.num_id, 'name': user.first_name, 'visit': 0, 'away': 0, 'overtime': 0, 'year': 0\
		, 'work': 0, 'marry': 0, 'maternity': 0, 'sick': 0, 'bereavement': 0, 'other': 0}
		try:
			month_obj = MonthApply.objects.get(user=user, year_month=year_month)
		except:
			errlog.error('导出文件错误，该申请人不存在月申请记录：'+traceback.format_exc())
			continue
		udict.update({'month_apply': month_obj.apply_day, 'add': month_obj.add_day})
		applys = Apply.objects.filter(user=user, end_date__range=(apply_start_date, apply_end_date), result=1)
		for obj in applys:
			if obj.leavetype.name == '外访':
				udict['visit'] = udict['visit'] + obj.total_day
			if obj.leavetype.name == '出差':
				udict['away'] = udict['away'] + obj.total_day
			if obj.leavetype.name == '调休':
				udict['overtime'] = udict['overtime'] + obj.total_day
			if obj.leavetype.name == '年假':
				udict['year'] = udict['year'] + obj.total_day
			if obj.leavetype.name == '事假':
				udict['work'] = udict['work'] + obj.total_day
			# if obj.leavetype.name == '加班':
			# 	udict['add'] = udict['add'] + obj.total_day
			if obj.leavetype.name == '婚假':
				udict['marry'] = udict['marry'] + obj.total_day
			if obj.leavetype.name == '产假':
				udict['maternity'] = udict['maternity'] + obj.total_day
			if obj.leavetype.name == '病假':
				udict['sick'] = udict['sick'] + obj.total_day
			if obj.leavetype.name == '丧假':
				udict['bereavement'] = udict['bereavement'] + obj.total_day
			if obj.leavetype.name == '其他':
				udict['other'] = udict['other'] + obj.total_day
		write_list.append(udict)

	wb = Workbook(encoding='utf-8')  
	sheet1 = wb.add_sheet(u"本月记录")  
	sheet1.write(0, 0, u"员工编号")  
	sheet1.write(0, 1, u"申请人")  
	sheet1.write(0, 2, u"外访")  
	sheet1.write(0, 3, u"出差")
	sheet1.write(0, 4, u"调休")  
	sheet1.write(0, 5, u"年假")  
	sheet1.write(0, 6, u"事假")  
	sheet1.write(0, 7, u"加班")  
	sheet1.write(0, 8, u"婚假")  
	sheet1.write(0, 9, u"产假")  
	sheet1.write(0, 10, u"病假")  
	sheet1.write(0, 11, u"丧假")  
	sheet1.write(0, 12, u"其他")
	sheet1.write(0, 13, u"本月申请总天数")
	sheet1_row = 1  
	for obj in write_list:
		sheet1.write(sheet1_row, 0, obj['id_num'])  
		sheet1.write(sheet1_row, 1, obj['name'])  
		sheet1.write(sheet1_row, 2, obj['visit'])
		sheet1.write(sheet1_row, 3, obj['away'])
		sheet1.write(sheet1_row, 4, obj['overtime'])
		sheet1.write(sheet1_row, 5, obj['year'])
		sheet1.write(sheet1_row, 6, obj['work'])
		sheet1.write(sheet1_row, 7, obj['add'])
		sheet1.write(sheet1_row, 8, obj['marry'])
		sheet1.write(sheet1_row, 9, obj['maternity'])
		sheet1.write(sheet1_row, 10, obj['sick'])
		sheet1.write(sheet1_row, 11, obj['bereavement'])
		sheet1.write(sheet1_row, 12, obj['other'])
		sheet1.write(sheet1_row, 13, obj['month_apply'])
		sheet1_row += 1
	io = StringIO.StringIO()
	wb.save(io)  
	io.seek(0)
	response.write(io.getvalue()) 
	return response



