# -*-coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Record(models.Model):
    duration_choice = (
        (1, '全天'),
        (0, '半天'),
    )
    user = models.ForeignKey(User, related_name='records')
    inTime = models.DateTimeField("上班时间", null=True, blank=True)
    outTime = models.DateTimeField("下班时间", null=True, blank=True)
    isLate = models.BooleanField('是否迟到', default=False)
    isEarly = models.BooleanField('是否早退', default=False)
    allTime = models.CharField('总时长', max_length=16, default='', blank=True)
    createDate = models.DateField(null=True, blank=True)

    PunchOut = models.BooleanField('打卡缺失', default=False, blank=True)
    isDinner = models.BooleanField('是否订餐', default=False)
    isWorkDay = models.BooleanField('是否是工作日', default=False)

    class Meta:
        ordering = ['-createDate', '-allTime']
        verbose_name = '考勤'
        verbose_name_plural = '考勤记录'

    def __unicode__(self):
        return self.user.first_name

    def get_absolute_url(self):
        return reverse('check_detail', kwargs={'pk': self.pk})


class CheckInOut(models.Model):
    emId = models.CharField("员工编号", max_length=32, default='')
    checkTime = models.DateTimeField("打卡时间")

    class Meta:
        ordering = ['-id']
        verbose_name = '卡机数据'
        verbose_name_plural = '卡机数据'

    def __unicode__(self):
        return self.emId


class CheckTotal(models.Model):
    user = models.ForeignKey(User, related_name='checktotal')
    workDay = models.FloatField("出勤天数", null=True, blank=True)
    totalTime = models.FloatField("总工作时长", null=True, blank=True)
    avgTime = models.FloatField("平均工作时长", null=True, blank=True)
    addWorkTime = models.FloatField("加班时长", null=True, blank=True)
    avgAddWorkTime = models.FloatField("平均加班时长", null=True, blank=True)
    lateInTimes = models.IntegerField("迟到次数", null=True, blank=True)
    earlyOutTimes = models.IntegerField("早退次数", null=True, blank=True)
    dinnerTimes = models.IntegerField("订餐次数", null=True, blank=True)
    PunchOutTimes = models.IntegerField("打卡缺失次数", null=True, blank=True)
    function = models.IntegerField("功能数", null=True, blank=True)
    task = models.IntegerField("任务数", null=True, blank=True)
    bug = models.IntegerField("BUG数", null=True, blank=True)
    defect = models.IntegerField("线上缺陷", null=True, blank=True)
    createDate = models.CharField(max_length=20, null=True, blank=True)

    score = models.CharField("分数", max_length=20, null=True, blank=True)
    comment = models.CharField("评价", max_length=20, null=True, blank=True)

    class Meta:
        ordering = ['-createDate', '-totalTime', '-addWorkTime', '-avgAddWorkTime', '-avgAddWorkTime']
        verbose_name = '月绩效'
        verbose_name_plural = '月绩效'

    def __unicode__(self):
        return self.user.first_name

    def get_absolute_url(self):
        return reverse('check_total_detail', kwargs={'pk': self.pk})
