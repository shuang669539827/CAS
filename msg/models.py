# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import F
from django.contrib.auth.models import User

from cas.models import Project

# Create your models here.


class Messages(models.Model):
    subject = models.CharField(max_length=125, default='', blank=True, verbose_name='标题')
    description = models.CharField(max_length=255, default='', blank=True, verbose_name='描述')
    app = models.CharField(max_length=125, default='', blank=True, verbose_name='应用')
    sender = models.ForeignKey(User, null=True, blank=True, related_name='sended', verbose_name='发送者')
    accepter = models.ManyToManyField(User, blank=True, verbose_name='接收者')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='读取时间')
    deal_at = models.DateTimeField(null=True, blank=True, verbose_name='处理时间')
    pushtype = models.IntegerField(null=True, blank=True, verbose_name='推送类型', help_text='0:所有, 1:cas')
    dealtype = models.IntegerField(null=True, blank=True, verbose_name='处理类型', help_text='0:点击即删除, 1:通过接口删除')
    status = models.BooleanField(default=False)

    mid = models.IntegerField(null=True, blank=True, verbose_name='关联模型id')
    mname = models.CharField(max_length=125, default='', blank=True, verbose_name='关联模型表名')
    url = models.URLField(max_length=125, blank=True, null=True, verbose_name='跳转地址')

    class Meta:
        ordering = ['-id']
        verbose_name = '消息'
        verbose_name_plural = '消息'

    def save(self, accepter=None, *args, **kwargs):
        super(Messages, self).save(*args, **kwargs)
        self.accepter.add(*accepter)
        for u in self.accepter.all():
            Counter.objects.get_or_create(user=u)
        objs = Counter.objects.filter(user__in=self.accepter.all())
        objs.update(count=F('count') + 1)

    def delete(self, *args, **kwargs):
        for u in self.accepter.all():
            Counter.objects.get_or_create(user=u)
        objs = Counter.objects.filter(user__in=self.accepter.all())
        objs.update(count=F('count') - 1)
        super(Messages, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        if self.app in [obj.name for obj in Project.objects.all()]:
            pro = Project.objects.get(name=self.app)
            server = pro.url
            if self.dealtype == 0:
                self.delete()
            return "/login/?service=%s&forward=%s" % (server, self.url)
        else:
            return self.url


class Counter(models.Model):
    user = models.OneToOneField(User, null=True, blank=True)
    count = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '统计'
        verbose_name_plural = '统计'
