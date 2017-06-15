# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Apply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name=b'\xe8\xb5\xb7\xe5\xa7\x8b\xe6\x97\xa5\xe6\x9c\x9f')),
                ('end_date', models.DateField(verbose_name=b'\xe7\xbb\x93\xe6\x9d\x9f\xe6\x97\xa5\xe6\x9c\x9f')),
                ('upfile', models.FileField(max_length=500, null=True, upload_to=b'file/%Y/%m', blank=True)),
                ('half', models.IntegerField(blank=True, null=True, verbose_name=b'\xe5\x8d\x8a\xe5\xa4\xa9,\xe5\x85\xa8\xe5\xa4\xa9', choices=[(0, b'\xe5\x8d\x8a\xe5\xa4\xa9'), (1, b'\xe5\x85\xa8\xe5\xa4\xa9')])),
                ('desc', models.TextField(max_length=1000, null=True, verbose_name=b'\xe7\x94\xb3\xe8\xaf\xb7\xe7\x90\x86\xe7\x94\xb1', blank=True)),
                ('apply_date', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe7\x94\xb3\xe8\xaf\xb7\xe6\x97\xa5\xe6\x9c\x9f')),
                ('total_day', models.FloatField(null=True, verbose_name=b'\xe5\x90\x88\xe8\xae\xa1\xe5\xa4\xa9\xe6\x95\xb0', blank=True)),
                ('status', models.BooleanField(default=False, verbose_name=b'\xe5\xae\xa1\xe6\x89\xb9\xe7\x8a\xb6\xe6\x80\x81')),
                ('result', models.IntegerField(blank=True, null=True, verbose_name=b'\xe5\xae\xa1\xe6\x89\xb9\xe7\xbb\x93\xe6\x9e\x9c', choices=[(0, b'\xe6\x8b\x92\xe7\xbb\x9d'), (1, b'\xe5\x90\x8c\xe6\x84\x8f'), (2, b'\xe5\xb7\xb2\xe5\x8f\x96\xe6\xb6\x88')])),
            ],
            options={
                'ordering': ['-apply_date'],
                'verbose_name': '\u7533\u8bf7\u5355',
                'verbose_name_plural': '\u7533\u8bf7\u5355\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'\xe7\xb1\xbb\xe5\x9e\x8b\xe5\x90\x8d\xe7\xa7\xb0')),
                ('include_day', models.IntegerField(null=True, verbose_name=b'\xe5\x8c\x85\xe5\x90\xab\xe5\x87\xa0\xe5\xa4\xa9\xe5\x81\x87\xe6\x9c\x9f', blank=True)),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x88\xab\xe5\x90\x8d', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u5047\u671f\u7c7b\u578b',
                'verbose_name_plural': '\u5047\u671f\u7c7b\u578b\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='MonthApply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year_month', models.CharField(max_length=100, null=True, verbose_name=b'\xe5\xbd\x93\xe5\x89\x8d\xe5\xb9\xb4\xe6\x9c\x88', blank=True)),
                ('add_day', models.FloatField(default=0, verbose_name=b'\xe9\x9d\x9e\xe5\xb7\xa5\xe4\xbd\x9c\xe6\x97\xa5\xe5\x8a\xa0\xe7\x8f\xad', blank=True)),
                ('apply_day', models.FloatField(default=0, verbose_name=b'\xe6\x9c\xac\xe6\x9c\x88\xe7\x94\xb3\xe8\xaf\xb7', blank=True)),
                ('user', models.ForeignKey(verbose_name=b'\xe4\xb8\xaa\xe4\xba\xba', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u6708\u7533\u8bf7\u8bb0\u5f55',
                'verbose_name_plural': '\u6708\u7533\u8bf7\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='UserHoliday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year_day', models.FloatField(default=0, verbose_name=b'\xe5\xb9\xb4\xe5\x81\x87', blank=True)),
                ('overtime_day', models.FloatField(default=0, verbose_name=b'\xe8\xb0\x83\xe4\xbc\x91', blank=True)),
                ('user', models.OneToOneField(verbose_name=b'\xe4\xb8\xaa\xe4\xba\xba', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u4e2a\u4eba\u5047\u671f\u7edf\u8ba1',
                'verbose_name_plural': '\u4e2a\u4eba\u5047\u671f\u7edf\u8ba1\u5217\u8868',
            },
        ),
        migrations.AddField(
            model_name='apply',
            name='leavetype',
            field=models.ForeignKey(verbose_name=b'\xe5\x81\x87\xe6\x9c\x9f\xe7\xb1\xbb\xe5\x9e\x8b', to='leave.LeaveType'),
        ),
        migrations.AddField(
            model_name='apply',
            name='user',
            field=models.ForeignKey(verbose_name=b'\xe7\x94\xb3\xe8\xaf\xb7\xe4\xba\xba', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='monthapply',
            unique_together=set([('user', 'year_month')]),
        ),
    ]
