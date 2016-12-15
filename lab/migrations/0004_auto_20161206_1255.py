# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0003_auto_20161127_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='result',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
        ),
    ]
