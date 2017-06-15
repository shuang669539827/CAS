# -*- coding: utf-8 -*-
import datetime
import math
import calendar
from collections import OrderedDict

from django.views.generic import DetailView, ListView
from django.utils.http import urlencode
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from single_sign.maxin import LoginRequiredMixin
from .models import Record, CheckTotal
from cas.models import Pro
from leave.models import Apply
from .tasks import get_work_num


class CheckShow(LoginRequiredMixin, ListView):
    model = Record
    paginate_by = 20
    template_name = 'checkin-list.html'

    def get_queryset(self):
        queryset = super(CheckShow, self).get_queryset()
        self.type = self.request.GET.get('type', 'self').lower()
        self.username = self.request.GET.get('username', '').lower()
        self.nowdate = self.request.GET.get('nowdate', '').lower()
        if self.type == 'self':
            if self.nowdate:
                queryset = queryset.filter(user=self.request.user, createDate=datetime.datetime.strptime(self.nowdate, '%Y-%m-%d'))
            else:
                queryset = queryset.filter(user=self.request.user).order_by("-createDate")
        elif self.type == 'subordinates':
            if self.nowdate:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first(), createDate=datetime.datetime.strptime(self.nowdate, '%Y-%m-%d'))
                else:
                    queryset = queryset.filter(user__in=[p.user for p in self.request.user.super.all().filter(user__username__contains='.').exclude(user__is_active=False)], createDate=datetime.datetime.strptime(self.nowdate, '%Y-%m-%d'))
            else:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first()).order_by("-createDate")
                else:
                    queryset = queryset.filter(user__in=[p.user for p in self.request.user.super.all().filter(user__username__contains='.').exclude(user__is_active=False)]).order_by("-createDate")
        elif self.type == 'department':
            if self.nowdate:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first(),
                                               createDate=datetime.datetime.strptime(self.nowdate, '%Y-%m-%d'))
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(user__is_active=False)],
                                               createDate=datetime.datetime.strptime(self.nowdate, '%Y-%m-%d'))
            else:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first()).order_by(
                        "-createDate")
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(user__is_active=False)]).order_by(
                        "-createDate")
        else:
            raise Http404
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CheckShow, self).get_context_data()
        context['type'] = self.type
        context['nowdate'] = self.nowdate
        context['username'] = self.username
        context['subordinates'] = self.request.user.super.all().filter(user__username__contains='.').exclude(user__is_active=False)
        context['department'] = Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(user__is_active=False)
        context['extra_url_param'] = urlencode({'type': self.type, 'nowdate': self.nowdate, 'username': self.username})
        return context


class CheckDetail(LoginRequiredMixin, DetailView):
    model = Record
    context_object_name = 'obj'
    template_name = 'checkin-detail.html'

    def get_context_data(self, **kwargs):
        context = super(CheckDetail, self).get_context_data()
        leave = Apply.objects.filter(user=self.object.user, start_date__lte=self.object.createDate, end_date__gte=self.object.createDate).exclude(status=True, result__in=[0, 2])
        if leave.count() == 0:
            isleave, leavetype, duration = '否', '', ''
        elif leave.count() == 1:
            isleave = '是'
            leavetype = leave.first().leavetype.name
            if math.modf(leave.first().total_day)[0] == 0:
                duration = '全天'
            else:
                if leave.first().half == 0:
                    duration = '半天' if leave.first().end_date == self.object.createDate else '全天'
                else:
                    duration = '半天' if leave.first().start_date == self.object.createDate else '全天'
        else:
            isleave = '是'
            leavetype = ','.join([t[0] for t in leave.values_list('leavetype__name')])
            duration = '全天'
        context['leaveinfo'] = (isleave, leavetype, duration)
        return context


class CheckTotalView(LoginRequiredMixin, ListView):
    model = CheckTotal
    paginate_by = 20
    template_name = 'checkin-total-list.html'

    def get_queryset(self):
        queryset = super(CheckTotalView, self).get_queryset()
        self.type = self.request.GET.get('type', 'self').lower()
        self.username = self.request.GET.get('username', '').lower()
        self.nowdate = self.request.GET.get('nowdate', '').lower()
        if self.type == 'self':
            if self.nowdate:
                queryset = queryset.filter(user=self.request.user, createDate=self.nowdate + '-01')
            else:
                queryset = queryset.filter(user=self.request.user).order_by("-createDate")
        elif self.type == 'subordinates':
            if self.nowdate:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first(),
                                               createDate=self.nowdate + '-01')
                else:
                    queryset = queryset.filter(user__in=[p.user for p in self.request.user.super.all().filter(
                        user__username__contains='.').exclude(num_id='').exclude(user__is_active=False)]
                        , createDate=self.nowdate + '-01')
            else:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first()).order_by(
                        "-createDate")
                else:
                    queryset = queryset.filter(user__in=[p.user for p in self.request.user.super.all().filter(
                        user__username__contains='.').exclude(num_id='').exclude(num_id='').exclude(user__is_active=False)]).order_by(
                        "-createDate")
        elif self.type == 'department':
            if self.nowdate:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first(),
                                               createDate=self.nowdate + '-01')
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(num_id='').exclude(user__is_active=False)],
                                               createDate=self.nowdate + '-01')
            else:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first()).order_by(
                        "-createDate")
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(num_id='').exclude(user__is_active=False)]).order_by(
                        "-createDate")
        elif self.type == 'all':
            if self.nowdate:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first(),
                                               createDate=self.nowdate + '-01')
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(user__username__contains='.').exclude(num_id='').exclude(
                                               user__is_active=False)], createDate=self.nowdate + '-01')
            else:
                if self.username:
                    queryset = queryset.filter(user=User.objects.filter(username=self.username).first()).order_by(
                        "-createDate")
                else:
                    queryset = queryset.filter(user__in=[p.user for p in Pro.objects.filter(user__username__contains='.').exclude(num_id='').exclude(
                        user__is_active=False)]).order_by("-createDate")
        else:
            raise Http404
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CheckTotalView, self).get_context_data()
        context['type'] = self.type
        context['nowdate'] = self.nowdate
        context['username'] = self.username
        context['subordinates'] = self.request.user.super.all().filter(user__username__contains='.').exclude(user__is_active=False).exclude(num_id='')
        context['department'] = Pro.objects.filter(department=self.request.user.pro.department, user__username__contains='.').exclude(user__is_active=False).exclude(num_id='')
        context['allpro'] = Pro.objects.filter(user__username__contains='.').exclude(user__is_active=False).exclude(num_id='')
        context['extra_url_param'] = urlencode({'type': self.type, 'nowdate': self.nowdate, 'username': self.username})
        return context


class CheckTotalDetail(LoginRequiredMixin, DetailView):
    model = CheckTotal
    context_object_name = 'obj'
    template_name = 'checkin-total-detail.html'

    def get_leave_days(self):
        year = int(self.object.createDate.split('-')[0])
        month = int(self.object.createDate.split('-')[1])
        dic = OrderedDict([("jiaban", 0), ("waifang", 0), ("chuchai", 0), ("bingjia", 0), ("tiaoxiu", 0), ("nianjia", 0), ("shijia", 0)
                          , ("hunjia", 0), ("chajia", 0), ("sangjia", 0), ("qita", 0)])
        for day in range(1, calendar.monthrange(year, month)[1]+1):
            if len(str(day)) == 1:
                today = datetime.datetime.strptime(self.object.createDate[:8] + '0' + str(day), "%Y-%m-%d")
            else:
                today = datetime.datetime.strptime(self.object.createDate[:8] + str(day), "%Y-%m-%d")
            leave = Apply.objects.filter(user=self.object.user, start_date__lte=today,
                                         end_date__gte=today).exclude(status=True, result__in=[0, 2])
            if leave.count() == 0:
                types, days = None, 0
            elif leave.count() == 1:
                types = leave.first().leavetype.en_name
                if math.modf(leave.first().total_day)[0] == 0:
                    days = 1
                else:
                    if leave.first().half == 0:
                        days = 0.5 if leave.first().end_date == today else 1
                    else:
                        days = 0.5 if leave.first().start_date == today else 1
            else:
                types = ','.join([t[0] for t in leave.values_list('leavetype__en_name')])
                days = 0.5
            if types:
                leavetype = types.split(',')
                for tp in leavetype:
                    dic[tp] += days
        return dic

    def get_context_data(self, **kwargs):
        context = super(CheckTotalDetail, self).get_context_data()

        now_month = datetime.datetime.strptime(self.object.createDate, '%Y-%m-%d')
        next_month = datetime.datetime.strptime(self.object.createDate, '%Y-%m-%d') + datetime.timedelta(days=40)
        pros, _ = get_work_num(self.object.user.username, now_month, next_month)
        projects = []
        for k, v in pros.items():
            v.update({'project': k})
            projects.append(v)
        context['projects'] = projects
        context['leave'] = self.get_leave_days().values()
        return context


@login_required
def grade(request, obj_id):
    score = request.GET.get('score')
    comment = request.GET.get('comment')
    obj = CheckTotal.objects.get(pk=obj_id)
    obj.score = score
    obj.comment = comment
    obj.save()
    return JsonResponse({'code': 0})


