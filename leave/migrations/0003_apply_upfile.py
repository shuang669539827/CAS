# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0002_remove_apply_upfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='apply',
            name='upfile',
            field=models.FileField(default=1, max_length=500, upload_to=b'file/%Y/%m'),
            preserve_default=False,
        ),
    ]
