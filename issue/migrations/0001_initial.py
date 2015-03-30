# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import regex_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assertion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('check_function', models.TextField()),
                ('name', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.TextField()),
                ('details', jsonfield.fields.JSONField(null=True, blank=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Resolved'), (2, 'Wont_fix')], default=0)),
                ('resolved_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IssueAction',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('execution_time', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField(default=True)),
                ('details', jsonfield.fields.JSONField(null=True, blank=True)),
                ('issue', models.ForeignKey(to='issue.Issue', related_name='executed_actions')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelAssertion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('check_function', models.TextField()),
                ('name', models.TextField()),
                ('model_type', models.ForeignKey(to='contenttypes.ContentType', related_name='+')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelIssue',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.TextField()),
                ('details', jsonfield.fields.JSONField(null=True, blank=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Resolved'), (2, 'Wont_fix')], default=0)),
                ('resolved_time', models.DateTimeField(null=True, blank=True)),
                ('record_id', models.PositiveIntegerField(default=0)),
                ('record_type', models.ForeignKey(null=True, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Responder',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('watch_pattern', regex_field.fields.RegexField(max_length=128, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResponderAction',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('delay_sec', models.IntegerField()),
                ('target_function', models.TextField()),
                ('function_kwargs', jsonfield.fields.JSONField(default={})),
                ('responder', models.ForeignKey(to='issue.Responder', related_name='actions')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='issueaction',
            name='responder_action',
            field=models.ForeignKey(to='issue.ResponderAction'),
            preserve_default=True,
        ),
    ]
