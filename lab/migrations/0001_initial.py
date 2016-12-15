# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import opal.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('opal', '0025_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('status', models.CharField(blank=True, max_length=256, null=True, choices=[(b'pending', b'pending'), (b'complete', b'complete')])),
                ('lab_test_type', models.CharField(max_length=256, null=True, blank=True)),
                ('date_ordered', models.DateField(null=True, blank=True)),
                ('date_received', models.DateField(null=True, blank=True)),
                ('extras', jsonfield.fields.JSONField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_lab_labtest_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('patient', models.ForeignKey(to='opal.Patient')),
                ('resistant_antibiotics', models.ManyToManyField(related_name='test_resistant', to='opal.Antimicrobial')),
                ('sensitive_antibiotics', models.ManyToManyField(related_name='test_sensitive', to='opal.Antimicrobial')),
                ('updated_by', models.ForeignKey(related_name='updated_lab_labtest_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('consistency_token', models.CharField(max_length=8)),
                ('observation_type', models.CharField(max_length=256)),
                ('extras', jsonfield.fields.JSONField(null=True, blank=True)),
                ('result', models.CharField(max_length=256, null=True, blank=True)),
                ('name', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(related_name='created_lab_observation_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('lab_test', models.ForeignKey(related_name='observations', to='lab.LabTest')),
                ('updated_by', models.ForeignKey(related_name='updated_lab_observation_subrecords', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(opal.models.UpdatesFromDictMixin, opal.models.ToDictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Antimicrobial',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='DynamicLookupList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='DynamicResultChoices',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='GenericInput',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='PendingPosNeg',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='PosNeg',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='PosNegEquivicalNotDone',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
        migrations.CreateModel(
            name='PosNegUnknown',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('lab.observation',),
        ),
    ]
