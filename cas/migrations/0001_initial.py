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
            name='ApplyPerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(default=b'', max_length=200, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', blank=True)),
                ('project', models.CharField(default=b'', max_length=200, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae', blank=True)),
                ('role', models.CharField(default=b'', max_length=200, verbose_name=b'\xe8\xa7\x92\xe8\x89\xb2', blank=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False)),
                ('result', models.IntegerField(blank=True, null=True, verbose_name=b'\xe5\xae\xa1\xe6\x89\xb9\xe7\xbb\x93\xe6\x9e\x9c', choices=[(0, b'\xe6\x8b\x92\xe7\xbb\x9d'), (1, b'\xe5\x90\x8c\xe6\x84\x8f')])),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u6743\u9650\u7533\u8bf7',
                'verbose_name_plural': '\u6743\u9650\u7533\u8bf7\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, verbose_name=b'\xe9\x83\xa8\xe9\x97\xa8')),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x8f\x8c\xe7\xb4\xa2\xe5\xbc\x95', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u90e8\u95e8',
                'verbose_name_plural': '\u90e8\u95e8\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'\xe5\xaf\xbc\xe8\x88\xaa')),
                ('url', models.CharField(max_length=100, verbose_name=b'\xe6\x8f\x8f\xe8\xbf\xb0')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u5bfc\u822a\u83dc\u5355',
                'verbose_name_plural': '\u5bfc\u822a\u83dc\u5355',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'\xe6\x96\xb0\xe9\x97\xbb')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u65b0\u95fb\u5217\u8868',
                'verbose_name_plural': '\u65b0\u95fb\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num_id', models.CharField(default=b'', max_length=100, verbose_name=b'\xe5\x91\x98\xe5\xb7\xa5\xe7\xbc\x96\xe5\x8f\xb7', blank=True)),
                ('sex', models.IntegerField(default=0, verbose_name=b'\xe6\x80\xa7\xe5\x88\xab', choices=[(0, b'\xe7\x94\xb7'), (1, b'\xe5\xa5\xb3')])),
                ('floor', models.IntegerField(default=1, verbose_name=b'\xe6\xa5\xbc\xe5\xb1\x82', choices=[(1, b'2F'), (2, b'20F'), (3, b'\xe7\x9f\xb3\xe6\x99\xaf\xe5\xb1\xb1')])),
                ('work_year', models.IntegerField(default=0, verbose_name=b'\xe5\xb7\xa5\xe9\xbe\x84(\xe5\xb9\xb4)', blank=True)),
                ('id_num', models.CharField(default=b'', max_length=100, verbose_name=b'\xe8\xba\xab\xe4\xbb\xbd\xe8\xaf\x81\xe5\x8f\xb7', blank=True)),
                ('birth', models.CharField(default=b'', max_length=100, verbose_name=b'\xe7\x94\x9f\xe6\x97\xa5', blank=True)),
                ('birthadd', models.CharField(default=b'', max_length=100, verbose_name=b'\xe7\xb1\x8d\xe8\xb4\xaf', blank=True)),
                ('in_time', models.DateField(null=True, verbose_name=b'\xe5\x85\xa5\xe8\x81\x8c\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('qq', models.CharField(default=b'', max_length=100, verbose_name=b'QQ', blank=True)),
                ('phone', models.CharField(default=b'', max_length=200, verbose_name=b'\xe8\x81\x94\xe7\xb3\xbb\xe7\x94\xb5\xe8\xaf\x9d', blank=True)),
                ('vercode', models.CharField(default=b'', max_length=200, verbose_name=b'\xe9\xaa\x8c\xe8\xaf\x81\xe7\xa0\x81', blank=True)),
                ('add_role_perm', models.BooleanField(default=False, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe8\xa7\x92\xe8\x89\xb2\xe6\x9d\x83\xe9\x99\x90')),
                ('vacation_manager', models.BooleanField(default=False, verbose_name=b'\xe5\x81\x87\xe6\x9c\x9f\xe7\xae\xa1\xe7\x90\x86\xe6\x9d\x83\xe9\x99\x90')),
                ('dinner_manager', models.BooleanField(default=False, verbose_name=b'\xe8\xae\xa2\xe9\xa4\x90\xe7\xae\xa1\xe7\x90\x86\xe6\x9d\x83\xe9\x99\x90')),
                ('user_manger', models.BooleanField(default=False, verbose_name=b'CAS\xe7\x94\xa8\xe6\x88\xb7\xe7\xae\xa1\xe7\x90\x86')),
                ('apply_subject_perm', models.BooleanField(default=False, verbose_name=b'CAS\xe5\xae\xa1\xe6\x89\xb9\xe9\xa1\xb9\xe7\x9b\xae\xe7\x94\xb3\xe8\xaf\xb7\xe6\x9d\x83\xe9\x99\x90')),
                ('department', models.ForeignKey(verbose_name=b'\xe9\x83\xa8\xe9\x97\xa8', blank=True, to='cas.Department', null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u7528\u6237',
                'verbose_name_plural': '\u7528\u6237\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x90\x8d\xe7\xa7\xb0')),
                ('url', models.CharField(unique=True, max_length=128, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe5\x9c\xb0\xe5\x9d\x80')),
                ('desc', models.CharField(max_length=128, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe6\x8f\x8f\xe8\xbf\xb0')),
                ('user', models.ForeignKey(verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe7\xbb\xb4\xe6\x8a\xa4\xe4\xba\xba', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u9879\u76ee',
                'verbose_name_plural': '\u9879\u76ee\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae\xe8\xa7\x92\xe8\x89\xb2')),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x8f\x8c\xe7\xb4\xa2\xe5\xbc\x95', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u9879\u76ee\u89d2\u8272',
                'verbose_name_plural': '\u9879\u76ee\u89d2\u8272',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.URLField()),
                ('ticket', models.CharField(max_length=256)),
                ('created', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name=b'ticket_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x8f\x8c\xe7\xb4\xa2\xe5\xbc\x95', blank=True)),
                ('project', models.ForeignKey(verbose_name=b'\xe9\xa1\xb9\xe7\x9b\xae', to='cas.Project')),
                ('projectrole', models.ManyToManyField(to='cas.ProjectRole', null=True, verbose_name=b'\xe8\xa7\x92\xe8\x89\xb2', blank=True)),
                ('user', models.ForeignKey(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u9879\u76ee\u89d2\u8272\u5173\u7cfb',
                'verbose_name_plural': '\u9879\u76ee\u89d2\u8272\u5173\u7cfb\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, verbose_name=b'\xe8\xa7\x92\xe8\x89\xb2')),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x8f\x8c\xe7\xb4\xa2\xe5\xbc\x95', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u4eba\u7269\u89d2\u8272',
                'verbose_name_plural': '\u4eba\u7269\u89d2\u8272',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=60, verbose_name=b'\xe5\x8c\xba\xe5\x9f\x9f\xe5\x90\x8d\xe5\xad\x97')),
                ('name_id', models.IntegerField(unique=True, null=True, verbose_name=b'\xe5\x8f\x8c\xe7\xb4\xa2\xe5\xbc\x95', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u533a\u57df',
                'verbose_name_plural': '\u533a\u57df\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pro',
            name='permission',
            field=models.ManyToManyField(to='cas.Project', null=True, verbose_name=b'\xe8\xae\xbf\xe9\x97\xae\xe9\xa1\xb9\xe7\x9b\xae\xe6\x9d\x83\xe9\x99\x90', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pro',
            name='role',
            field=models.ForeignKey(verbose_name=b'\xe8\x81\x8c\xe4\xbd\x8d', blank=True, to='cas.UserRole', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pro',
            name='superior',
            field=models.ForeignKey(related_name=b'super', verbose_name=b'\xe4\xb8\x8a\xe7\xba\xa7', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pro',
            name='user',
            field=models.OneToOneField(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pro',
            name='zone',
            field=models.ForeignKey(verbose_name=b'\xe5\x8c\xba\xe5\x9f\x9f', blank=True, to='cas.Zone', null=True),
            preserve_default=True,
        ),
    ]
