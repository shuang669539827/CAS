#coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from cas.models import Pro
import os



# class Type(models.Model):
#     """docstring for Type"""
#     ch_name = models.CharField(max_length=200, blank=False, null=False, unique=True, verbose_name='中文名称')
#     en_name = models.CharField(max_length=200, blank=False, null=False, unique=True, verbose_name='英文名称')
#     create_time = models.DateField(auto_now_add=True)

#     class Meta:
#        verbose_name = '类型列表'
#        verbose_name_plural = '类型列表'
#        ordering = ["-create_time"]

#     def __unicode__(self):
#         return u'%s' % os.path.basename(self.ch_name)


class Food(models.Model):
    name = models.CharField(max_length=200, blank=False, null=False, unique=True, verbose_name='中文名称')
    info = models.CharField(max_length=500, blank=True, null=True, verbose_name='描述')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
       verbose_name = '食物列表'
       verbose_name_plural = '食物列表'
       ordering = ["-create_time"]

    def __unicode__(self):
        return u'%s' % os.path.basename(self.name)


class Orders(models.Model):
    pro = models.ForeignKey(Pro)
    food = models.ForeignKey(Food)
    create_time = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = '订单列表'
        verbose_name_plural = "订单列表"
        ordering = ['-create_time']
                
    def __unicode__(self):
        return u'%s : %s' %(self.pro.user.first_name, self.create_time)


        
