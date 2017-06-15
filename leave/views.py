# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import StringIO
import logging
import datetime
import time
import math
import traceback
import calendar
import os
import sys
import urlparse
from xlwt import *

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.utils.http import urlencode
from django.utils.timezone import now
from django.db.models import Q

from .models import Apply, UserHoliday, MonthApply, LeaveType
from workflow.models import Transition, State, WorkflowHistory
from single_sign.maxin import LoginRequiredMixin
from workflow.exceptions import *
from msg.models import Messages
from celerymail import send_html_mail

reload(sys)
sys.setdefaultencoding('utf8')

errlog = logging.getLogger('daserr')
api_res = {"20170101": "2", "20170102": "1", "20170103": "0", "20170104": "0", "20170105": "0", "20170106": "0",
           "20170107": "1", "20170108": "1", "20170109": "0", "20170110": "0", "20170111": "0", "20170112": "0",
           "20170113": "0", "20170114": "1", "20170115": "1", "20170116": "0", "20170117": "0", "20170118": "0",
           "20170119": "0", "20170120": "0", "20170121": "1", "20170122": "0", "20170123": "0", "20170124": "0",
           "20170125": "0", "20170126": "0", "20170127": "2", "20170128": "2", "20170129": "2", "20170130": "1",
           "20170131": "1", "20170201": "1", "20170202": "1", "20170203": "0", "20170204": "0", "20170205": "1",
           "20170206": "0", "20170207": "0", "20170208": "0", "20170209": "0", "20170210": "0", "20170211": "1",
           "20170212": "1", "20170213": "0", "20170214": "0", "20170215": "0", "20170216": "0", "20170217": "0",
           "20170218": "1", "20170219": "1", "20170220": "0", "20170221": "0", "20170222": "0", "20170223": "0",
           "20170224": "0", "20170225": "1", "20170226": "1", "20170227": "0", "20170228": "0", "20170229": "0",
           "20170230": "0", "20170231": "0", "20170301": "0", "20170302": "0", "20170303": "0", "20170304": "1",
           "20170305": "1", "20170306": "0", "20170307": "0", "20170308": "0", "20170309": "0", "20170310": "0",
           "20170311": "1", "20170312": "1", "20170313": "0", "20170314": "0", "20170315": "0", "20170316": "0",
           "20170317": "0", "20170318": "1", "20170319": "1", "20170320": "0", "20170321": "0", "20170322": "0",
           "20170323": "0", "20170324": "0", "20170325": "1", "20170326": "1", "20170327": "0", "20170328": "0",
           "20170329": "0", "20170330": "0", "20170331": "0", "20170401": "0", "20170402": "1", "20170403": "1",
           "20170404": "2", "20170405": "0", "20170406": "0", "20170407": "0", "20170408": "1", "20170409": "1",
           "20170410": "0", "20170411": "0", "20170412": "0", "20170413": "0", "20170414": "0", "20170415": "1",
           "20170416": "1", "20170417": "0", "20170418": "0", "20170419": "0", "20170420": "0", "20170421": "0",
           "20170422": "1", "20170423": "1", "20170424": "0", "20170425": "0", "20170426": "0", "20170427": "0",
           "20170428": "0", "20170429": "1", "20170430": "1", "20170431": "0", "20170501": "2", "20170502": "0",
           "20170503": "0", "20170504": "0", "20170505": "0", "20170506": "1", "20170507": "1", "20170508": "0",
           "20170509": "0", "20170510": "0", "20170511": "0", "20170512": "0", "20170513": "1", "20170514": "1",
           "20170515": "0", "20170516": "0", "20170517": "0", "20170518": "0", "20170519": "0", "20170520": "1",
           "20170521": "1", "20170522": "0", "20170523": "0", "20170524": "0", "20170525": "0", "20170526": "0",
           "20170527": "0", "20170528": "1", "20170529": "1", "20170530": "2", "20170531": "0", "20170601": "0",
           "20170602": "0", "20170603": "1", "20170604": "1", "20170605": "0", "20170606": "0", "20170607": "0",
           "20170608": "0", "20170609": "0", "20170610": "1", "20170611": "1", "20170612": "0", "20170613": "0",
           "20170614": "0", "20170615": "0", "20170616": "0", "20170617": "1", "20170618": "1", "20170619": "0",
           "20170620": "0", "20170621": "0", "20170622": "0", "20170623": "0", "20170624": "1", "20170625": "1",
           "20170626": "0", "20170627": "0", "20170628": "0", "20170629": "0", "20170630": "0", "20170631": "0",
           "20170701": "1", "20170702": "1", "20170703": "0", "20170704": "0", "20170705": "0", "20170706": "0",
           "20170707": "0", "20170708": "1", "20170709": "1", "20170710": "0", "20170711": "0", "20170712": "0",
           "20170713": "0", "20170714": "0", "20170715": "1", "20170716": "1", "20170717": "0", "20170718": "0",
           "20170719": "0", "20170720": "0", "20170721": "0", "20170722": "1", "20170723": "1", "20170724": "0",
           "20170725": "0", "20170726": "0", "20170727": "0", "20170728": "0", "20170729": "1", "20170730": "1",
           "20170731": "0", "20170801": "0", "20170802": "0", "20170803": "0", "20170804": "0", "20170805": "1",
           "20170806": "1", "20170807": "0", "20170808": "0", "20170809": "0", "20170810": "0", "20170811": "0",
           "20170812": "1", "20170813": "1", "20170814": "0", "20170815": "0", "20170816": "0", "20170817": "0",
           "20170818": "0", "20170819": "1", "20170820": "1", "20170821": "0", "20170822": "0", "20170823": "0",
           "20170824": "0", "20170825": "0", "20170826": "1", "20170827": "1", "20170828": "0", "20170829": "0",
           "20170830": "0", "20170831": "0", "20170901": "0", "20170902": "1", "20170903": "1", "20170904": "0",
           "20170905": "0", "20170906": "0", "20170907": "0", "20170908": "0", "20170909": "1", "20170910": "1",
           "20170911": "0", "20170912": "0", "20170913": "0", "20170914": "0", "20170915": "0", "20170916": "1",
           "20170917": "1", "20170918": "0", "20170919": "0", "20170920": "0", "20170921": "0", "20170922": "0",
           "20170923": "1", "20170924": "1", "20170925": "0", "20170926": "0", "20170927": "0", "20170928": "0",
           "20170929": "0", "20170930": "0", "20170931": "0", "20171001": "2", "20171002": "1", "20171003": "1",
           "20171004": "2", "20171005": "1", "20171006": "1", "20171007": "1", "20171008": "1", "20171009": "0",
           "20171010": "0", "20171011": "0", "20171012": "0", "20171013": "0", "20171014": "1", "20171015": "1",
           "20171016": "0", "20171017": "0", "20171018": "0", "20171019": "0", "20171020": "0", "20171021": "1",
           "20171022": "1", "20171023": "0", "20171024": "0", "20171025": "0", "20171026": "0", "20171027": "0",
           "20171028": "1", "20171029": "1", "20171030": "0", "20171031": "0", "20171101": "0", "20171102": "0",
           "20171103": "0", "20171104": "1", "20171105": "1", "20171106": "0", "20171107": "0", "20171108": "0",
           "20171109": "0", "20171110": "0", "20171111": "1", "20171112": "1", "20171113": "0", "20171114": "0",
           "20171115": "0", "20171116": "0", "20171117": "0", "20171118": "1", "20171119": "1", "20171120": "0",
           "20171121": "0", "20171122": "0", "20171123": "0", "20171124": "0", "20171125": "1", "20171126": "1",
           "20171127": "0", "20171128": "0", "20171129": "0", "20171130": "0", "20171131": "0", "20171201": "0",
           "20171202": "1", "20171203": "1", "20171204": "0", "20171205": "0", "20171206": "0", "20171207": "0",
           "20171208": "0", "20171209": "1", "20171210": "1", "20171211": "0", "20171212": "0", "20171213": "0",
           "20171214": "0", "20171215": "0", "20171216": "1", "20171217": "1", "20171218": "0", "20171219": "0",
           "20171220": "0", "20171221": "0", "20171222": "0", "20171223": "1", "20171224": "1", "20171225": "0",
           "20171226": "0", "20171227": "0", "20171228": "0", "20171229": "0", "20171230": "1", "20171231": "1"}
api_key = (
    u'20170103', u'20170104', u'20170105', u'20170106', u'20170109', u'20170110', u'20170111', u'20170112', u'20170113',
    u'20170116', u'20170117', u'20170118', u'20170119', u'20170120', u'20170122', u'20170123', u'20170124', u'20170125',
    u'20170126', u'20170203', u'20170204', u'20170206', u'20170207', u'20170208', u'20170209', u'20170210', u'20170213',
    u'20170214', u'20170215', u'20170216', u'20170217', u'20170220', u'20170221', u'20170222', u'20170223', u'20170224',
    u'20170227', u'20170228', u'20170229', u'20170230', u'20170231', u'20170301', u'20170302', u'20170303', u'20170306',
    u'20170307', u'20170308', u'20170309', u'20170310', u'20170313', u'20170314', u'20170315', u'20170316', u'20170317',
    u'20170320', u'20170321', u'20170322', u'20170323', u'20170324', u'20170327', u'20170328', u'20170329', u'20170330',
    u'20170331', u'20170401', u'20170405', u'20170406', u'20170407', u'20170410', u'20170411', u'20170412', u'20170413',
    u'20170414', u'20170417', u'20170418', u'20170419', u'20170420', u'20170421', u'20170424', u'20170425', u'20170426',
    u'20170427', u'20170428', u'20170431', u'20170502', u'20170503', u'20170504', u'20170505', u'20170508', u'20170509',
    u'20170510', u'20170511', u'20170512', u'20170515', u'20170516', u'20170517', u'20170518', u'20170519', u'20170522',
    u'20170523', u'20170524', u'20170525', u'20170526', u'20170527', u'20170531', u'20170601', u'20170602', u'20170605',
    u'20170606', u'20170607', u'20170608', u'20170609', u'20170612', u'20170613', u'20170614', u'20170615', u'20170616',
    u'20170619', u'20170620', u'20170621', u'20170622', u'20170623', u'20170626', u'20170627', u'20170628', u'20170629',
    u'20170630', u'20170703', u'20170704', u'20170705', u'20170706', u'20170707', u'20170710', u'20170711',
    u'20170712', u'20170713', u'20170714', u'20170717', u'20170718', u'20170719', u'20170720', u'20170721', u'20170724',
    u'20170725', u'20170726', u'20170727', u'20170728', u'20170731', u'20170801', u'20170802', u'20170803', u'20170804',
    u'20170807', u'20170808', u'20170809', u'20170810', u'20170811', u'20170814', u'20170815', u'20170816', u'20170817',
    u'20170818', u'20170821', u'20170822', u'20170823', u'20170824', u'20170825', u'20170828', u'20170829', u'20170830',
    u'20170831', u'20170901', u'20170904', u'20170905', u'20170906', u'20170907', u'20170908', u'20170911', u'20170912',
    u'20170913', u'20170914', u'20170915', u'20170918', u'20170919', u'20170920', u'20170921', u'20170922', u'20170925',
    u'20170926', u'20170927', u'20170928', u'20170929', u'20170930', u'20171009', u'20171010', u'20171011',
    u'20171012', u'20171013', u'20171016', u'20171017', u'20171018', u'20171019', u'20171020', u'20171023', u'20171024',
    u'20171025', u'20171026', u'20171027', u'20171030', u'20171031', u'20171101', u'20171102', u'20171103', u'20171106',
    u'20171107', u'20171108', u'20171109', u'20171110', u'20171113', u'20171114', u'20171115', u'20171116', u'20171117',
    u'20171120', u'20171121', u'20171122', u'20171123', u'20171124', u'20171127', u'20171128', u'20171129', u'20171130',
    u'20171201', u'20171204', u'20171205', u'20171206', u'20171207', u'20171208', u'20171211', u'20171212', u'20171213',
    u'20171214', u'20171215', u'20171218', u'20171219', u'20171220', u'20171221', u'20171222', u'20171225',
    u'20171226', u'20171227', u'20171228', u'20171229')


class ApplyView(View):

    def _repeat(self, start, end, half, apply_days, repeat=False):
        nowdate = start
        while True:
            objs = Apply.objects.filter(start_date__lte=nowdate, end_date__gte=nowdate, user=self.request.user).exclude(status=True, result__in=[0, 2])
            if objs.count() == 1:
                if math.modf(objs.first().total_day)[0] == 0:
                    repeat = True
                    break
                else:
                    if not half and apply_days != 0.5:
                        repeat = True
                        break
                    else:
                        if objs.first().half == 1 and half == '0' and objs.first().start_date == end:
                            pass
                        elif objs.first().half == 0 and half == '1' and objs.first().end_date == start:
                            pass
                        else:
                            repeat = True
                            break
            elif objs.count() > 1:
                repeat = True
                break
            if (end - nowdate).days == 0:
                break
            nowdate += datetime.timedelta(days=1)
        return repeat

    def get(self, request):
        num = request.user.super.count()
        types = LeaveType.objects.all()
        start_date = str(datetime.datetime.now().date())
        return render(request, 'leave-apply.html', {'num': num, 'types': types, "start_date": start_date})

    def post(self, request):
        user = request.user
        leavetype = request.POST.get('leavetype', '其他')
        apply_type = LeaveType.objects.get(name=leavetype)
        apply_file = request.FILES.get('apply_file')
        start_date = request.POST.get('start_date')
        apply_days = float(request.POST.get('apply_days', '0'))
        apply_info = request.POST.get('apply_info', '')
        apply_visitor = request.POST.get('apply_visitor', '')
        apply_address = request.POST.get('apply_address', '')
        chanjiatype = request.POST.get('chanjiatype', '')
        half = request.POST.get('sore', None)

        try:
            d1 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({'msg': '日期格式有误'})

        if leavetype == '年假':
            today = datetime.date.today()
            if (today - request.user.pro.in_time).days < 90:
                return JsonResponse({'msg': '试用期未过，不能申请'})
            if d1.strftime("%Y%m%d") not in api_key:
                return JsonResponse({'msg': '开始日期为非工作日，不能申请'})
            holiday_obj = UserHoliday.objects.get(user=user)
            if apply_days > holiday_obj.year_day:
                return JsonResponse({'msg': '年假剩余天数不足，不能申请'})

        if leavetype == '调休':
            if d1.strftime("%Y%m%d") not in api_key:
                return JsonResponse({'msg': '开始日期为非工作日，不能申请'})
            holiday_obj = UserHoliday.objects.get(user=user)
            if apply_days > holiday_obj.overtime_day:
                return JsonResponse({'msg': '调休剩余天数不足，不能申请'})

        if leavetype == '外访':
            d2 = d1 + datetime.timedelta(days=math.ceil(apply_days) - 1)
            apply_desc = '客户：%s;  地点：%s;  备注：%s;' % (apply_visitor, apply_address, apply_info)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=apply_days, desc=apply_desc)

        elif leavetype == '出差':
            d2 = d1 + datetime.timedelta(days=math.ceil(apply_days) - 1)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=apply_days,
                        desc=apply_info, upfile=apply_file)

        elif leavetype == '产假':
            if d1.strftime("%Y%m%d") not in api_key:
                return JsonResponse({'msg': '开始日期为非工作日，不能申请'})
            if chanjiatype == '1':
                apply_desc = '产假类型：产检假1天，备注：%s' % apply_info
                num = 0
                d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                while True:
                    end_date = d2.strftime('%Y%m%d')
                    if api_res[end_date] == "0":
                        num += 1
                    if num >= 1:
                        break
                    d2 = d2 + datetime.timedelta(days=1)
            elif chanjiatype == '15':
                apply_desc = '产假类型：产检假15天，备注：%s' % apply_info
                d2 = d1 + datetime.timedelta(days=14)
            else:
                apply_desc = '产假类型：产检假128天，备注：%s' % apply_info
                d2 = d1 + datetime.timedelta(days=127)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=int(chanjiatype),
                        desc=apply_desc, upfile=apply_file)

        elif leavetype == '婚假':
            if d1.strftime("%Y%m%d") not in api_key:
                return JsonResponse({'msg': '开始日期为非工作日，不能申请'})
            d2 = d1 + datetime.timedelta(days=9)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=10,
                        desc=apply_info, upfile=apply_file)

        elif leavetype == '加班':
            num = 0
            d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            while True:
                end_date = d2.strftime('%Y%m%d')
                if api_res[end_date] in ["1", "2"]:
                    num += 1
                if num >= apply_days:
                    break
                d2 = d2 + datetime.timedelta(days=1)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=apply_days,
                        desc=apply_info)

        else:
            if d1.strftime("%Y%m%d") not in api_key:
                return JsonResponse({'msg': '开始日期为非工作日，不能申请'})
            num = 0
            d2 = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            while True:
                end_date = d2.strftime('%Y%m%d')
                if api_res[end_date] == "0":
                    num += 1
                if num >= apply_days:
                    break
                d2 = d2 + datetime.timedelta(days=1)
            obj = Apply(user=user, start_date=d1, end_date=d2,
                        leavetype=apply_type, total_day=apply_days,
                        desc=apply_info, upfile=apply_file)
        if self._repeat(d1, d2, half, apply_days):
            return JsonResponse({'msg': '该日期区间已经申请过'})
        if half:
            obj.half = int(half)
        obj.save()
        obj.create(request.user)
        return JsonResponse({'msg': 0})


class LeaveNotes(LoginRequiredMixin, ListView):
    model = Apply
    paginate_by = 20
    context_object_name = 'notes'
    template_name = 'leave-notes.html'

    def get_queryset(self):
        # users = [obj.user for obj in self.request.user.super.all()]
        # users.append(self.request.user)
        queryset = super(LeaveNotes, self).get_queryset()
        self.status = self.request.GET.get('status', 'approvaling').lower()
        self.type = self.request.GET.get('type', 'my').lower()

        if self.type == 'my':
            if self.status == 'approvaling':
                queryset = queryset.filter(user=self.request.user, status=False)
            else:
                queryset = queryset.filter(user=self.request.user, status=True)
        else:
            queryset = queryset.exclude(user=self.request.user).filter(workflowactivity__participants__user=self.request.user)
            if self.status == 'approvaling':
                queryset = queryset.exclude(~Q(workflowactivity__current_state__users=self.request.user),
                                            label='leave-glc') \
                                .exclude(~Q(workflowactivity__created_by__pro__department__user=self.request.user),
                                         label='leave-department') \
                                .exclude(~Q(workflowactivity__created_by__pro__superior=self.request.user), label='leave-pro') \
                                .exclude(~Q(workflowactivity__created_by=self.request.user), label='leave-start') \
                                .exclude(status=True)
            else:
                queryset = queryset.exclude(workflowactivity__current_state__users=self.request.user, label='leave-glc') \
                                .exclude(workflowactivity__created_by__pro__superior=self.request.user, label='leave-pro') \
                                .exclude(workflowactivity__created_by=self.request.user, label='leave-start') \
                                .exclude(workflowactivity__created_by__pro__department__user=self.request.user,
                                         label='leave-department')
        return queryset.select_related('workflowactivity', 'workflowactivity__current_state').all()

    def get_context_data(self, **kwargs):
        context = super(LeaveNotes, self).get_context_data(**kwargs)
        """前三次传输(通过,拒绝)的权限需要赋予任何人"""
        startran = Transition.objects.filter(label__in=['leave-start', 'leave-department3',
                                                        'leave-pro3', 'leave-department2',
                                                        'leave-pro2', 'leave-department1',
                                                        'leave-pro1'])
        for t in startran:
            t.users.add(self.request.user)
            t.save()
        context['num'] = self.request.user.super.count()
        context['status'] = self.status
        context['type'] = self.type
        context['extra_url_param'] = urlencode({'status': self.status, 'type': self.type})
        return context


class NoteDetail(LoginRequiredMixin, DetailView):
    model = Apply
    context_object_name = 'note'
    template_name = 'leave-notedetail.html'

    def getlasthis(self, his):
        if not his[0].transition:
            return self.getlasthis(his[1:])
        else:
            return his[0]

    def get_context_data(self, **kwargs):
        context = super(NoteDetail, self).get_context_data(**kwargs)
        # 定义可以执行操作的人
        his = list(self.object.workflowactivity.history.all())
        lasthis = self.getlasthis(his)

        def find_last(obj, num):
            if obj.count() < 2:
                return num
            try:
                value = api_key.index(obj[0].start_date.strftime('%Y%m%d')) - api_key.index(obj[1].end_date.strftime('%Y%m%d'))
            except ValueError:
                return num
            if value == 1:
                num += obj[1].total_day
                return find_last(obj[1:], num)
            else:
                return num

        if self.object.leavetype.name in ['加班', '出差', '外访']:
            context['transitions'] = self.object.has_perm_use_transitions(self.request.user) \
                .exclude(label='leave-pro1')
        else:
            objs = Apply.objects.filter(user=self.object.user, apply_date__lte=self.object.apply_date).exclude(
                result__in=[0, 2]).exclude(leavetype__in=LeaveType.objects.filter(name__in=['加班', '出差', '外访']))
            total = find_last(objs, self.object.total_day) if objs.count() > 1 else self.object.total_day
            if lasthis.transition.label == 'leave-start':
                if total <= 2:
                    context['transitions'] = self.object.has_perm_use_transitions(self.request.user) \
                        .exclude(label='leave-pro1')
                else:
                    context['transitions'] = self.object.has_perm_use_transitions(self.request.user) \
                        .exclude(label='leave-pro2')
            elif lasthis.transition.label == 'leave-pro1':
                if total <= 5:
                    context['transitions'] = self.object.has_perm_use_transitions(self.request.user) \
                        .exclude(label='leave-department1')
                else:
                    context['transitions'] = self.object.has_perm_use_transitions(self.request.user) \
                        .exclude(label='leave-department2')
            else:
                context['transitions'] = self.object.has_perm_use_transitions(self.request.user)
        return context


@login_required
def notesearch(request):
    num = request.user.super.count()
    year_month = request.POST.get('search')
    try:
        year = int(year_month.split('-')[0])
        month = int(year_month.split('-')[1])
        objs = Apply.objects.filter(user=request.user, apply_date__year=year, apply_date__month=month)
    except:
        errlog.info('查询记录错误:' + traceback.format_exc())
        return HttpResponseRedirect('/leave/notes/')
    return render(request, 'leave-notes.html', {'objs': objs, 'num': num})


@login_required
def myholiday(request):
    show = request.GET.get('show', 'my').lower()
    year_month = datetime.datetime.strftime(datetime.date.today(), "%Y%m")
    if show == "my":
        my_holiday, _ = UserHoliday.objects.get_or_create(user=request.user)
        my_apply, _ = MonthApply.objects.get_or_create(user=request.user, year_month=year_month)
        objs = [(my_holiday, my_apply)]
        for pro in request.user.super.all():
            holiday_obj, _ = UserHoliday.objects.get_or_create(user=pro.user)
            monthapply_obj, _ = MonthApply.objects.get_or_create(user=pro.user, year_month=year_month)
            objs.append((holiday_obj, monthapply_obj))
    else:
        objs = []
        for u in User.objects.all():
            holiday_obj, _ = UserHoliday.objects.get_or_create(user=u)
            monthapply_obj, _ = MonthApply.objects.get_or_create(user=u, year_month=year_month)
            objs.append((holiday_obj, monthapply_obj))
    return render(request, 'leave-myholiday.html', {'objs': objs,
                                                    'extra_url_param': urlencode({'show': show}),
                                                    'show': show})


@login_required
def manager(request):
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    year_month = str(year) + '0' + str(month) if month < 10 else str(year) + str(month)
    month_objs = MonthApply.objects.filter(year_month=year_month, apply_day__gte=0).exclude(apply_day=0)
    return render(request, 'leave-manager1.html', {'month_objs': month_objs})


class ApprovaledList(LoginRequiredMixin, ListView):
    model = Apply
    template_name = 'leave-manager2.html'
    paginate_by = 15
    context_object_name = 'page'

    def get_queryset(self):
        queryset = super(ApprovaledList, self).get_queryset().filter(status=True, result=1, user__username__contains='.')
        self.name = self.request.GET.get('firstname', '')
        if self.name:
            user_list = User.objects.filter(first_name__contains=self.name)
            queryset = queryset.filter(user__in=user_list)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ApprovaledList, self).get_context_data()
        context['firstname'] = self.name
        context['extra_url_param'] = urlencode({'firstname': self.name})
        return context


class ApprovalingList(LoginRequiredMixin, ListView):
    model = Apply
    template_name = 'leave-manager3.html'
    paginate_by = 15
    context_object_name = 'page'

    def get_queryset(self):
        queryset = super(ApprovalingList, self).get_queryset().filter(status=False, user__username__contains='.')
        self.name = self.request.GET.get('firstname', '')
        if self.name:
            user_list = User.objects.filter(first_name__contains=self.name)
            queryset = queryset.filter(user__in=user_list)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ApprovalingList, self).get_context_data()
        context['firstname'] = self.name
        context['extra_url_param'] = urlencode({'firstname': self.name})
        return context


@login_required
def managersearch2(request):
    user = request.user
    num = user.super.count()
    name = request.POST.get('search')
    try:
        user_list = User.objects.filter(first_name__contains=name)
        page = Apply.objects.filter(user__in=user_list, status=True, result=1)
    except:
        errlog.error('查询错误:' + traceback.format_exc())
        return HttpResponseRedirect('/leave/manager2/')
    return render(request, 'leave-manager2.html', {'user': user, 'page': page, 'num': num})


@login_required
def managersearch3(request):
    user = request.user
    num = user.super.count()
    name = request.POST.get('search')
    try:
        user_list = User.objects.filter(first_name__contains=name)
        page = Apply.objects.filter(user__in=user_list, status=False)
    except:
        errlog.error('查询错误:' + traceback.format_exc())
        return HttpResponseRedirect('/leave/manager3/')
    return render(request, 'leave-manager3.html', {'user': user, 'page': page, 'num': num})


@login_required
def down(request):
    obj_id = request.GET.get('obj_id')
    obj = Apply.objects.get(id=obj_id)
    fn = obj.upfile.path
    filename = str(os.path.split(fn)[1])
    _, end = os.path.splitext(filename)
    now = time.strftime('%Y%m%d', time.localtime())

    def readfile(fp, buf_size=262144):
        f = open(fp, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()

    response = StreamingHttpResponse(readfile(fn), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(now + end)
    return response


@login_required
def write_approvaled(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="approvaled.xls"'

    current_time = datetime.datetime.now()
    last_month = datetime.datetime.strftime(current_time - datetime.timedelta(days=56), '%Y%m')
    last_time = datetime.datetime.strptime(last_month + '01', '%Y%m%d')

    objs = Apply.objects.filter(apply_date__range=(last_time, current_time), status=True, result=1)

    wb = Workbook(encoding='utf-8')
    sheet1 = wb.add_sheet(u"已审批记录")
    sheet1.write(0, 0, u"员工编号")
    sheet1.write(0, 1, u"申请人")
    sheet1.write(0, 2, u"假期类型")
    sheet1.write(0, 3, u"开始时间")
    sheet1.write(0, 4, u"结束时间")
    sheet1.write(0, 5, u"总天数")
    sheet1.write(0, 6, u"理由")
    sheet1_row = 1
    for obj in objs:
        sheet1.write(sheet1_row, 0, obj.user.pro.num_id)
        sheet1.write(sheet1_row, 1, obj.user.first_name)
        sheet1.write(sheet1_row, 2, obj.leavetype.name)
        sheet1.write(sheet1_row, 3, obj.start_date.strftime('%Y-%m-%d'))
        sheet1.write(sheet1_row, 4, obj.end_date.strftime('%Y-%m-%d'))
        sheet1.write(sheet1_row, 5, obj.total_day)
        sheet1.write(sheet1_row, 6, obj.desc)
        sheet1_row += 1
    io = StringIO.StringIO()
    wb.save(io)
    io.seek(0)
    response.write(io.getvalue())
    return response


@login_required
def write_approvaling(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="approvaling.xls"'

    current_time = datetime.datetime.now()
    last_month = datetime.datetime.strftime(current_time - datetime.timedelta(days=56), '%Y%m')
    last_time = datetime.datetime.strptime(last_month + '01', '%Y%m%d')

    objs = Apply.objects.filter(apply_date__range=(last_time, current_time), status=False)

    wb = Workbook(encoding='utf-8')
    sheet1 = wb.add_sheet(u"待审批记录")
    sheet1.write(0, 0, u"员工编号")
    sheet1.write(0, 1, u"申请人")
    sheet1.write(0, 2, u"假期类型")
    sheet1.write(0, 3, u"开始时间")
    sheet1.write(0, 4, u"结束时间")
    sheet1.write(0, 5, u"总天数")
    sheet1.write(0, 6, u"理由")
    sheet1_row = 1
    for obj in objs:
        sheet1.write(sheet1_row, 0, obj.user.pro.num_id)
        sheet1.write(sheet1_row, 1, obj.user.first_name)
        sheet1.write(sheet1_row, 2, obj.leavetype.name)
        sheet1.write(sheet1_row, 3, obj.start_date.strftime('%Y-%m-%d'))
        sheet1.write(sheet1_row, 4, obj.end_date.strftime('%Y-%m-%d'))
        sheet1.write(sheet1_row, 5, obj.total_day)
        sheet1.write(sheet1_row, 6, obj.desc)
        sheet1_row += 1
    io = StringIO.StringIO()
    wb.save(io)
    io.seek(0)
    response.write(io.getvalue())
    return response


@login_required
def write_excel(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="monthnotes.xls"'

    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    month = 12 if month == 1 else month - 1
    year = year - 1 if month == 1 else year
    year_month = str(year) + '0' + str(month) if month < 10 else str(year) + str(month)
    write_list = []
    users = User.objects.select_related().all()

    for user in users:
        udict = {'编号': user.pro.num_id, '姓名': user.first_name,
                 '外访': 0, '出差': 0, '调休': 0, '年假': 0,
                 '事假': 0, '婚假': 0, '产假': 0, '病假': 0,
                 '丧假': 0, '其他': 0, '加班': 0}

        month_obj, _ = MonthApply.objects.get_or_create(user=user, year_month=year_month)

        udict.update({'month_apply': month_obj.apply_day})
        applys = Apply.objects.filter(user=user, start_date__month=month, result=1)
        applys_pre = Apply.objects.filter(user=user, end_date__month=month, start_date__month=12,
                                          result=1) if month == 1 else Apply.objects.filter(user=user,
                                                                                            end_date__month=month,
                                                                                            start_date__month=month - 1,
                                                                                            result=1)

        for obj in applys_pre:
            start_date = datetime.datetime.strftime(obj.start_date, '%Y%m%d')
            d1 = datetime.datetime.strptime(start_date, "%Y%m%d")
            month_total_days = calendar.monthrange(int(start_date[:4]), int(start_date[4:6]))[1]
            middle_date = start_date[:6] + str(month_total_days)
            """找出上个月的最后一个工作日日期"""
            while True:
                if obj.leavetype.name == '加班':
                    if api_res[middle_date] == '1':
                        break
                else:
                    if api_res[middle_date] == '0':
                        break
                month_total_days -= 1
                middle_date = start_date[:6] + str(month_total_days)
            d2 = datetime.datetime.strptime(middle_date, "%Y%m%d")
            now_month_days = (d2 - d1).days + 1
            next_month_days = obj.total_day - now_month_days
            if str(next_month_days)[-1] == '5':
                next_month_days += 0.5
            udict[obj.leavetype.name] += next_month_days

        for obj in applys:
            start_date = datetime.datetime.strftime(obj.start_date, '%Y%m%d')
            d1 = datetime.datetime.strptime(start_date, "%Y%m%d")
            end_date = datetime.datetime.strftime(obj.end_date, '%Y%m%d')
            if start_date[4:6] != end_date[4:6]:
                month_total_days = calendar.monthrange(int(start_date[:4]), int(start_date[4:6]))[1]
                middle_date = start_date[:6] + str(month_total_days)
                """找出本月的最后一个工作日日期"""
                while True:
                    if obj.leavetype.name == '加班':
                        if api_res[middle_date] == '1':
                            break
                    else:
                        if api_res[middle_date] == '0':
                            break
                    month_total_days -= 1
                    middle_date = start_date[:6] + str(month_total_days)
                d2 = datetime.datetime.strptime(middle_date, "%Y%m%d")
                now_month_days = (d2 - d1).days + 1
                next_month_days = obj.total_day - now_month_days
                if str(next_month_days)[-1] == '5':
                    now_month_days -= 0.5
                udict[obj.leavetype.name] += now_month_days
            else:
                udict[obj.leavetype.name] += obj.total_day
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


@login_required
def progress_transition(request, task_id):
    transaction_id = request.GET.get('transId')
    reason = request.GET.get('reason', '')

    if transaction_id is None:
        return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})
    try:
        task = Apply.objects.get(id=task_id)
    except Apply.DoesNotExist:
        return JsonResponse({'msg': 'Apply <%s> does not exist' % task_id})
    try:
        transaction = Transition.objects.get(id=int(transaction_id))
    except Transition.DoesNotExist:
        return JsonResponse({'msg': 'Transition <%s> does not exist' % transaction_id})

    try:
        task.workflowactivity.progress(transaction, request.user, note=reason)
    except WorkflowException as e:
        return JsonResponse({'msg': str(e)})

    return JsonResponse({'msg': 0})


@login_required
def force_stop(request, task_id):
    reason = request.GET.get('reason', '')
    try:
        task = Apply.objects.get(id=task_id)
    except Apply.DoesNotExist:
        return JsonResponse({'msg': 'Apply <%s> Does not exist' % task_id})

    state = State.objects.filter(name='撤销').first()

    task.workflowactivity.current_state = state
    task.workflowactivity.completed_on = now()
    task.workflowactivity.save()

    final_step = WorkflowHistory(
        workflowactivity=task.workflowactivity,
        state=task.workflowactivity.current_state,
        log_type=WorkflowHistory.COMMENT,
        note=reason,
        created_by=request.user,
    )
    final_step.save(reason=reason)

    task.status = True
    task.result = 2
    task.save()

    mail_receivers = [u.user.email for u in task.workflowactivity.participants.all()]
    message = '<h3>{title}</h3>' \
              '<a href="{link}">假期类型： {name}</a>' \
              '<p>申请人： {applicant}</p>' \
              '<p>状态描述： {desc}</p>' \
        .format(
        title='CAS - 假期提醒',
        name=task.leavetype.name,
        link=urlparse.urljoin(settings.MAIN_DOMAIN, task.get_absolute_url()),
        applicant=task.workflowactivity.created_by.get_full_name(),
        desc='撤销申请'
    )
    send_html_mail('CAS - 假期申请', message, mail_receivers)
    try:
        Messages.objects.get(app='请假', mid=task.pk).delete()
    except Messages.DoesNotExist:
        pass
    return JsonResponse({'msg': 0})
