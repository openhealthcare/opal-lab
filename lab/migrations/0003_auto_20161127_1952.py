# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0002_auto_20161127_1849'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labtest',
            old_name='details',
            new_name='extras',
        ),
        migrations.RenameField(
            model_name='observation',
            old_name='details',
            new_name='extras',
        ),
    ]
