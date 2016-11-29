# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labtest',
            old_name='extras',
            new_name='details',
        ),
        migrations.RenameField(
            model_name='observation',
            old_name='extras',
            new_name='details',
        ),
    ]
