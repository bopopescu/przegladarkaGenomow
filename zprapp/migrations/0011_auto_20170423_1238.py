# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-04-23 12:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zprapp', '0010_auto_20170419_2107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='aggregated_by',
        ),
        migrations.AddField(
            model_name='aggregation',
            name='annotation_slave',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='aggregated_by', to='zprapp.Annotation'),
            preserve_default=False,
        ),
    ]