# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-02 21:26
from __future__ import unicode_literals

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue', '0002_auto_20180329_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='details',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='issueaction',
            name='details',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='modelissue',
            name='details',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='responderaction',
            name='function_kwargs',
            field=models.JSONField(default={}, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
