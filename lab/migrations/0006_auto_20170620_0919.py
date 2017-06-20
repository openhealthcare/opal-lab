# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0005_auto_20161219_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labtest',
            old_name='date_ordered',
            new_name='datetime_ordered',
        ),
        migrations.RenameField(
            model_name='labtest',
            old_name='date_received',
            new_name='datetime_received',
        ),
    ]
