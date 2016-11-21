# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name=b'\xe4\xb8\xad\xe6\x96\x87\xe5\x90\x8d\xe7\xa7\xb0')),
                ('info', models.CharField(max_length=500, null=True, verbose_name=b'\xe6\x8f\x8f\xe8\xbf\xb0', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-create_time'],
                'verbose_name': '\u98df\u7269\u5217\u8868',
                'verbose_name_plural': '\u98df\u7269\u5217\u8868',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateField(auto_now_add=True)),
                ('food', models.ForeignKey(to='dinner.Food')),
                ('pro', models.ForeignKey(to='cas.Pro')),
            ],
            options={
                'ordering': ['-create_time'],
                'verbose_name': '\u8ba2\u5355\u5217\u8868',
                'verbose_name_plural': '\u8ba2\u5355\u5217\u8868',
            },
            bases=(models.Model,),
        ),
    ]
