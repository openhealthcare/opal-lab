# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import opal.models
from django.conf import settings
import opal.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0023_auto_20160630_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fk_name', models.CharField(max_length=250)),
                ('fk_module', models.CharField(max_length=250)),
                ('related_column', models.CharField(max_length=200)),
                ('result', models.CharField(max_length=250, null=True, blank=True)),
                ('datetime_received', models.DateTimeField(null=True, blank=True)),
                ('datetime_expected', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('status', models.CharField(max_length=250)),
                ('other', jsonfield.fields.JSONField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, opal.utils.AbstractBase),
        ),
        migrations.CreateModel(
            name='LabTestCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('fk_name', models.CharField(max_length=250)),
                ('fk_module', models.CharField(max_length=250)),
                ('other', jsonfield.fields.JSONField()),
                ('collection_name', models.CharField(max_length=250)),
                ('datetime_ordered', models.DateTimeField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_lab_labtestcollection_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('episode', models.ForeignKey(to='opal.Episode')),
                ('updated_by', models.ForeignKey(related_name='updated_lab_labtestcollection_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.AddField(
            model_name='labtest',
            name='collection',
            field=models.ForeignKey(to='lab.LabTestCollection'),
        ),
        migrations.CreateModel(
            name='HSV',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.labtest',),
        ),
        migrations.CreateModel(
            name='MicroTestCsfPcrCollection',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.labtestcollection',),
        ),
        migrations.CreateModel(
            name='VSV',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.labtest',),
        ),
    ]
