# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0003_apply_upfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apply',
            name='upfile',
            field=models.FileField(max_length=500, null=True, upload_to=b'file/%Y/%m', blank=True),
        ),
    ]
