# -*- coding:utf-8 -*-
from __future__ import absolute_import, division
import datetime
import pymssql as sql
import MySQLdb

from django.db.models import Avg, Sum

from celery import current_app as app
from celery.utils.log import get_task_logger

from cas.models import Pro
from leave.views import api_key
from .models import CheckInOut, Record, CheckTotal
from dinner.models import Orders


logger = get_task_logger(__name__)


def get_sql_data():
    today = datetime.date.today().strftime("%Y-%m-%d")
    last_day = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    conn = sql.connect(host='192.168.162.198', user='sa', password='bairong_2017', database='att2000')
    cur = conn.cursor()
    cur.execute(
        "select b.Badgenumber, a.CHECKTIME from CHECKINOUT a left join USERINFO b on a.userid = b.userid where \
         a.CHECKTIME between '{0:s}' and '{1:s}' order by a.CHECKTIME desc;".format(last_day, today))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


@app.task(name='checkin.input_sql_data', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def input_sql_data():
    data = get_sql_data()
    CheckInOut.objects.bulk_create([CheckInOut(emId=d[0], checkTime=d[1]) for d in data])


@app.task(name='checkin.input_record', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def input_record():
    last_day = datetime.date.today() - datetime.timedelta(days=1)
    Record.objects.filter(createDate=last_day).delete()
    today = datetime.date.today()
    for pro in Pro.objects.all().exclude(num_id=''):

        checkl = CheckInOut.objects.filter(emId=str(int(pro.num_id[2:])), checkTime__gte=last_day, checkTime__lt=today).order_by('checkTime')
        if last_day.strftime("%Y%m%d") in api_key:
            isworkday = True
            punchout = True if checkl.count() < 2 else False
        else:
            isworkday, punchout = False, False

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

        order = Orders.objects.filter(pro=pro, create_time=last_day).first()
        isdinner = True if order else False

        record = Record(user=pro.user, inTime=intime, outTime=outtime, allTime=alltime, isWorkDay=isworkday
                        , isLate=islate, isEarly=isearly, createDate=last_day, isDinner=isdinner, PunchOut=punchout
                        )
        record.save()


def get_work_num(username, last_month, now_month):
    last = last_month.strftime('%Y-%m') + '-01'
    now = now_month.strftime('%Y-%m') + '-01'
    conn = MySQLdb.connect('192.168.162.101', 'redmine_Select', 'RedMine_Select.2016.04.06', 'redmine', charset='utf8')
    cur = conn.cursor()
    cur.execute(
        "select project_id, (select name from projects where id = project_id)project_name,tracker_id ,count(1) as num from issues where id in (select distinct journalized_id from journals where created_on between '{0:s}' and '{1:s}'  and user_id = (select id from users where login='{2:s}'))  and status_id = 5 group by tracker_id,project_id;".format(last, now, username)
    )
    data = cur.fetchall()
    cur.close()
    conn.close()
    # tracker = {1: "错误", 2: "功能", 3: "任务", 4: "线上缺陷"}
    total = {1: 0, 2: 0, 3: 0, 4: 0}
    try:
        project = {d[1]: {1: 0, 2: 0, 3: 0, 4: 0} for d in data}
        for d in data:
            project[d[1]][d[2]] += d[3]
            total[d[2]] += d[3]
    except:
        project = {"total": {1: 0, 2: 0, 3: 0, 4: 0}}
    return project, total


@app.task(name='checkin.input_check_total', autoretry_for=(Exception,),
          max_retries=3, default_retry_delay=60, rate_limit='100/m')
def input_check_total():
    now_month = datetime.date.today()
    last_month = now_month - datetime.timedelta(days=20)
    CheckTotal.objects.filter(createDate=last_month.strftime("%Y-%m")).delete()
    for obj in Pro.objects.all().exclude(num_id=''):
        _, total = get_work_num(obj.user.username, last_month, now_month)
        records = Record.objects.filter(user=obj.user, createDate__year=last_month.year, createDate__month=last_month.month)
        workday = records.filter(isWorkDay=True).exclude(allTime='').count()
        totaltime = records.exclude(allTime='').aggregate(Sum('allTime')).get('allTime__sum')
        avgtime = format(totaltime / workday, '.2f') if totaltime and workday else 0

        addworktime = records.filter(isWorkDay=False).exclude(allTime='').aggregate(Sum('allTime')).get('allTime__sum') if records.filter(isWorkDay=False, allTime__isnull=False).aggregate(Sum('allTime')).get('allTime__sum') else 0
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
                                  , createDate=last_month.strftime("%Y-%m")+'-01'
                                  , PunchOutTimes=records.filter(PunchOut=True).count())
