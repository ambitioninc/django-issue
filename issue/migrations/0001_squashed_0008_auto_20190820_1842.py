# Generated by Django 2.2.4 on 2019-08-22 20:34

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import issue.migrations.datamigrations
import regex_field.fields


class Migration(migrations.Migration):

    replaces = [('issue', '0001_initial'), ('issue', '0002_auto_20180329_1522'), ('issue', '0003_auto_20180402_2126'), ('issue', '0004_auto_20181210_1857'), ('issue', '0005_responder_allow_retry'), ('issue', '0006_auto_20190820_1806'), ('issue', '0007_auto_20190820_1809'), ('issue', '0008_auto_20190820_1842')]

    initial = True

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assertion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_function', models.TextField()),
                ('name', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Resolved'), (2, 'Wont_fix')], default=0)),
                ('resolved_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelAssertion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_function', models.TextField()),
                ('name', models.TextField()),
                ('model_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Responder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('watch_pattern', regex_field.fields.RegexField(max_length=128, null=True)),
                ('allow_retry', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ResponderAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delay_sec', models.IntegerField()),
                ('target_function', models.TextField()),
                ('function_kwargs', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('responder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='issue.Responder')),
            ],
        ),
        migrations.CreateModel(
            name='ModelIssue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(0, 'Open'), (1, 'Resolved'), (2, 'Wont_fix')], default=0)),
                ('resolved_time', models.DateTimeField(blank=True, null=True)),
                ('record_id', models.PositiveIntegerField(default=0)),
                ('record_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IssueAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_time', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField(default=True)),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executed_actions', to='issue.Issue')),
                ('responder_action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issue.ResponderAction')),
                ('action_issue_id', models.PositiveIntegerField(null=True)),
                ('action_issue_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
            ],
        ),
        migrations.RunPython(
            code=issue.migrations.datamigrations.normalize_generic_issues,
        ),
        migrations.AlterField(
            model_name='issueaction',
            name='issue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='issue.Issue'),
        ),
    ]