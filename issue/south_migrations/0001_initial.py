# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Issue'
        db.create_table('issue_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('resolved_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('issue', ['Issue'])

        # Adding model 'ModelIssue'
        db.create_table('issue_modelissue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('resolved_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('record_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, to=orm['contenttypes.ContentType'])),
            ('record_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal('issue', ['ModelIssue'])

        # Adding model 'IssueAction'
        db.create_table('issue_issueaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executed_actions', to=orm['issue.Issue'])),
            ('responder_action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue.ResponderAction'])),
            ('execution_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal('issue', ['IssueAction'])

        # Adding model 'Responder'
        db.create_table('issue_responder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('watch_pattern', self.gf('regex_field.fields.RegexField')(max_length=128)),
        ))
        db.send_create_signal('issue', ['Responder'])

        # Adding model 'ResponderAction'
        db.create_table('issue_responderaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('responder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['issue.Responder'])),
            ('delay_sec', self.gf('django.db.models.fields.IntegerField')()),
            ('target_function', self.gf('django.db.models.fields.TextField')()),
            ('function_kwargs', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal('issue', ['ResponderAction'])

        # Adding model 'Assertion'
        db.create_table('issue_assertion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check_function', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('issue', ['Assertion'])

        # Adding model 'ModelAssertion'
        db.create_table('issue_modelassertion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check_function', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('model_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('issue', ['ModelAssertion'])


    def backwards(self, orm):
        # Deleting model 'Issue'
        db.delete_table('issue_issue')

        # Deleting model 'ModelIssue'
        db.delete_table('issue_modelissue')

        # Deleting model 'IssueAction'
        db.delete_table('issue_issueaction')

        # Deleting model 'Responder'
        db.delete_table('issue_responder')

        # Deleting model 'ResponderAction'
        db.delete_table('issue_responderaction')

        # Deleting model 'Assertion'
        db.delete_table('issue_assertion')

        # Deleting model 'ModelAssertion'
        db.delete_table('issue_modelassertion')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'issue.assertion': {
            'Meta': {'object_name': 'Assertion'},
            'check_function': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'issue.issue': {
            'Meta': {'object_name': 'Issue'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'resolved_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue.issueaction': {
            'Meta': {'object_name': 'IssueAction'},
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'execution_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executed_actions'", 'to': "orm['issue.Issue']"}),
            'responder_action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['issue.ResponderAction']"}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'issue.modelassertion': {
            'Meta': {'object_name': 'ModelAssertion'},
            'check_function': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['contenttypes.ContentType']"}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'issue.modelissue': {
            'Meta': {'object_name': 'ModelIssue'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'record_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'record_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'resolved_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'issue.responder': {
            'Meta': {'object_name': 'Responder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'watch_pattern': ('regex_field.fields.RegexField', [], {'max_length': '128'})
        },
        'issue.responderaction': {
            'Meta': {'object_name': 'ResponderAction'},
            'delay_sec': ('django.db.models.fields.IntegerField', [], {}),
            'function_kwargs': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['issue.Responder']"}),
            'target_function': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['issue']