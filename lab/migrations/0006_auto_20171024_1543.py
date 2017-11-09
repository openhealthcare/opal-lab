# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0005_auto_20161219_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labtest',
            name='resistant_antibiotics',
            field=models.ManyToManyField(related_name='test_resistant', to='opal.Antimicrobial', blank=True),
        ),
        migrations.AlterField(
            model_name='labtest',
            name='sensitive_antibiotics',
            field=models.ManyToManyField(related_name='test_sensitive', to='opal.Antimicrobial', blank=True),
        ),
    ]
