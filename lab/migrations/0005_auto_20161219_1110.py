# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0004_auto_20161206_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='external_identifier',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='labtest',
            name='external_system',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
