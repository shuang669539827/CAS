#coding:utf8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='类型名称')
    include_day = models.IntegerField(null=True, blank=True, verbose_name='包含几天假期')
    name_id = models.IntegerField(unique = True, null=True, blank=True, verbose_name='别名')
        
    class Meta:
        verbose_name = '假期类型'
        verbose_name_plural = '假期类型列表'
        ordering = ['-id']

    def __unicode__(self):
        return self.name


class Apply(models.Model):
    RESULT_NUM = (
        (0,'拒绝'),
        (1,'同意'),
        (2,'已取消'),
        )
    HALF_NUM = (
        (0, '半天'),
        (1, '全天'),
    )
    user = models.ForeignKey(User, verbose_name='申请人')
    start_date = models.DateField(verbose_name='起始日期')
    end_date = models.DateField(verbose_name='结束日期')
    leavetype = models.ForeignKey(LeaveType, verbose_name='假期类型')
    upfile = models.FileField(max_length=500, upload_to='file/%Y/%m', null=True, blank=True)
    half = models.IntegerField(choices=HALF_NUM, null=True, blank=True, verbose_name='半天,全天')
    desc = models.TextField(max_length=1000, null=True, blank=True, verbose_name='申请理由')
    apply_date = models.DateTimeField(auto_now_add=True, verbose_name='申请日期')
    total_day = models.FloatField(null=True, blank=True, verbose_name='合计天数')
    status = models.BooleanField(default=False, verbose_name="审批状态")
    result = models.IntegerField(choices=RESULT_NUM, null=True, blank=True, verbose_name="审批结果")

    class Meta:
    	verbose_name = '申请单'
        verbose_name_plural = '申请单列表'
        ordering = ['-apply_date']

    def __unicode__(self):
    	return '%s : %s'%(self.user.first_name, self.apply_date)


class UserHoliday(models.Model):
    user = models.OneToOneField(User, verbose_name='个人')
    year_day = models.FloatField(default=0, blank=True, verbose_name='年假')
    overtime_day = models.FloatField(default=0, blank=True, verbose_name='调休')
    

    class Meta:
        verbose_name = '个人假期统计'
        verbose_name_plural = '个人假期统计列表'
        ordering = ['-id']
    
    def __unicode__(self):
        return self.user.first_name


class MonthApply(models.Model):
    #每个月会进行一次更新
    user = models.ForeignKey(User, verbose_name='个人')
    year_month = models.CharField(max_length=100, null=True, blank=True, verbose_name='当前年月')
    add_day = models.FloatField(default=0, blank=True, verbose_name='非工作日加班')
    apply_day = models.FloatField(default=0, blank=True, verbose_name='本月申请')
    #free_day = models.FloatField(default=0, blank=True, verbose_name='')

    class Meta:
        verbose_name = '月申请记录'
        verbose_name_plural = '月申请记录'
        unique_together = ['user', 'year_month']
        ordering = ['-id']
    
    def __unicode__(self):
        return  '%s : %s'%(self.user.first_name, self.year_month)




