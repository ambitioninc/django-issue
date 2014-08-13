# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Issue'
        db.create_table(u'issue_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('resolved_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'issue', ['Issue'])

        # Adding model 'IssueNote'
        db.create_table(u'issue_issuenote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notes', to=orm['issue.Issue'])),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'issue', ['IssueNote'])

        # Adding model 'IssueAction'
        db.create_table(u'issue_issueaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executed_actions', to=orm['issue.Issue'])),
            ('responder_action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue.ResponderAction'])),
            ('execution_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'issue', ['IssueAction'])

        # Adding model 'Responder'
        db.create_table(u'issue_responder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('watch_pattern', self.gf('regex_field.fields.RegexField')(max_length=128)),
        ))
        db.send_create_signal(u'issue', ['Responder'])

        # Adding model 'ResponderAction'
        db.create_table(u'issue_responderaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('responder', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['issue.Responder'])),
            ('delay_sec', self.gf('django.db.models.fields.IntegerField')()),
            ('target_function', self.gf('django.db.models.fields.TextField')()),
            ('function_kwargs', self.gf('jsonfield.fields.JSONField')(default={})),
        ))
        db.send_create_signal(u'issue', ['ResponderAction'])

        # Adding model 'Assertion'
        db.create_table(u'issue_assertion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('check_function', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'issue', ['Assertion'])


    def backwards(self, orm):
        # Deleting model 'Issue'
        db.delete_table(u'issue_issue')

        # Deleting model 'IssueNote'
        db.delete_table(u'issue_issuenote')

        # Deleting model 'IssueAction'
        db.delete_table(u'issue_issueaction')

        # Deleting model 'Responder'
        db.delete_table(u'issue_responder')

        # Deleting model 'ResponderAction'
        db.delete_table(u'issue_responderaction')

        # Deleting model 'Assertion'
        db.delete_table(u'issue_assertion')


    models = {
        u'issue.assertion': {
            'Meta': {'object_name': 'Assertion'},
            'check_function': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'issue.issue': {
            'Meta': {'object_name': 'Issue'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'resolved_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'issue.issueaction': {
            'Meta': {'object_name': 'IssueAction'},
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'execution_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executed_actions'", 'to': u"orm['issue.Issue']"}),
            'responder_action': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['issue.ResponderAction']"}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'issue.issuenote': {
            'Meta': {'object_name': 'IssueNote'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': u"orm['issue.Issue']"})
        },
        u'issue.responder': {
            'Meta': {'object_name': 'Responder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'watch_pattern': ('regex_field.fields.RegexField', [], {'max_length': '128'})
        },
        u'issue.responderaction': {
            'Meta': {'object_name': 'ResponderAction'},
            'delay_sec': ('django.db.models.fields.IntegerField', [], {}),
            'function_kwargs': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': u"orm['issue.Responder']"}),
            'target_function': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['issue']