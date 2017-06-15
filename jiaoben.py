# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "single_sign.settings")
django.setup()
import pymssql as sql
import datetime
from django.utils.timezone import now

from leave.models import Apply
from workflow.models import WorkflowActivity, Workflow, State, WorkflowHistory, Transition

conn = sql.connect(host='192.168.162.198', user='sa', password='bairong_2017', database='att2000')

cur = conn.cursor()

cur.execute("select b.Badgenumber, a.CHECKTIME from CHECKINOUT a left join USERINFO b on a.userid = b.userid where a.CHECKTIME between '%s' and '%s' order by a.CHECKTIME ASC;"%('2017-05-01', '2017-06-14'))
data = cur.fetchall()

cur.close()
conn.close()


from __future__ import absolute_import, division
CheckInOut.objects.bulk_create([CheckInOut(emId=d[0], checkTime=d[1]) for d in data])
start = datetime.datetime(2017, 5, 1)
while True:
    if start.strftime("%Y-%m-%d") == '2017-06-14':
        break
    for pro in Pro.objects.all().exclude(num_id=''):

        if start.strftime("%Y%m%d") in api_key:
            isworkday = True
        else:
            isworkday = False

        checkl = CheckInOut.objects.filter(emId=str(int(pro.num_id[2:])), checkTime__gte=start,
                                           checkTime__lt=start+datetime.timedelta(days=1)).order_by('checkTime')
        if checkl.count() == 1:
            intime, outtime = checkl.first().checkTime, None
            isearly, islate, alltime = None, None, ''
        elif checkl.count() > 1:
            intime, outtime = checkl.first().checkTime, checkl.last().checkTime
            islate = True if intime.hour >= 10 and isworkday else False
            alltime = format((outtime - intime).seconds / 3600, '.2f')
            isearly = True if float(alltime) < 9 and isworkday else False
        else:
            intime, outtime, islate, alltime, isearly = None, None, None, '', None

        order = Orders.objects.filter(pro=pro, create_time=start).first()
        isdinner = True if order else False

        record = Record(user=pro.user, inTime=intime, outTime=outtime, allTime=alltime, isWorkDay=isworkday
                        , isLate=islate, isEarly=isearly, createDate=start, isDinner=isdinner
                        )
        record.save()
    start += datetime.timedelta(days=1)

now_month = datetime.date.today()
last_month = now_month - datetime.timedelta(days=20)
CheckTotal.objects.filter(createDate=last_month.strftime("%Y-%m")).delete()
for obj in Pro.objects.all().exclude(num_id=''):
    _, total = get_work_num(obj.user.username, last_month, now_month)
    records = Record.objects.filter(user=obj.user, createDate__year=last_month.year, createDate__month=last_month.month)
    workday = records.filter(isWorkDay=True).exclude(allTime='').count()
    totaltime = records.exclude(allTime='').aggregate(Sum('allTime')).get('allTime__sum')
    avgtime = format(totaltime / workday, '.2f') if totaltime and workday else 0

    addworktime = records.filter(isWorkDay=False).exclude(allTime='').aggregate(Sum('allTime')).get(
        'allTime__sum') if records.filter(isWorkDay=False, allTime__isnull=False).aggregate(Sum('allTime')).get(
        'allTime__sum') else 0
    for r in records.filter(isWorkDay=True).exclude(allTime=''):
        if float(r.allTime) > 9.5:
            addworktime += float(r.allTime) - 9.5
    addworktime *= 60
    avgaddworktime = format(addworktime / workday, '.2f') if addworktime else 0

    lateintimes = records.filter(isLate=True).count()
    earlyouttimes = records.filter(isEarly=True).count()
    CheckTotal.objects.create(user=obj.user, workDay=workday, totalTime=totaltime
                              , avgTime=avgtime, addWorkTime=addworktime, avgAddWorkTime=avgaddworktime
                              , lateInTimes=lateintimes, earlyOutTimes=earlyouttimes
                              , function=total[2], task=total[3], bug=total[1], defect=total[4]
                              , dinnerTimes=records.filter(isDinner=True).count()
                              , createDate=last_month.strftime("%Y-%m") + '-01')