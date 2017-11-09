# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import migrations, models


def change_to_datetime(apps, schema_editor):
    LabTest = apps.get_model('lab', 'LabTest')
    for lab_test in LabTest.objects.all():
        if lab_test.date_ordered:
            lab_test.datetime_ordered = datetime.datetime(
                lab_test.date_ordered.year,
                lab_test.date_ordered.month,
                lab_test.date_ordered.day
            )

        if lab_test.date_received:
            lab_test.datetime_received = datetime.datetime(
                lab_test.date_received.year,
                lab_test.date_received.month,
                lab_test.date_received.day
            )
        lab_test.save()


def change_to_date(apps, schema_editor):
    LabTest = apps.get_model('lab', 'LabTest')
    for lab_test in LabTest.objects.all():
        if lab_test.datetime_ordered:
            lab_test.date_ordered = datetime.date(
                lab_test.datetime_ordered.year,
                lab_test.datetime_ordered.month,
                lab_test.datetime_ordered.day
            )
        if lab_test.datetime_received:
            lab_test.date_received = datetime.datetime(
                lab_test.datetime_received.year,
                lab_test.datetime_received.month,
                lab_test.datetime_received.day
            )
        lab_test.save()


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0006_auto_20171024_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtest',
            name='datetime_ordered',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='labtest',
            name='datetime_received',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.RunPython(change_to_datetime, change_to_date),
        migrations.RemoveField(
            model_name='labtest',
            name='date_ordered',
        ),
        migrations.RemoveField(
            model_name='labtest',
            name='date_received',
        ),
    ]
