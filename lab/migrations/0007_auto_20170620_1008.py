# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0006_auto_20170620_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labtest',
            name='datetime_ordered',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='labtest',
            name='datetime_received',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
