# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class WhiteList(models.Model):
    filepath = models.CharField(max_length=255)
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name = '受限文件夹'
        verbose_name_plural = '受限文件夹列表'


class MaxSize(models.Model):
    size = models.IntegerField(default=15360000, blank=True)
