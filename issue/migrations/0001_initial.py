# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Note'
        db.create_table(u'issue_note', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('details', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'issue', ['Note'])

        # Adding model 'Issue'
        db.create_table(u'issue_issue', (
            (u'note_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['issue.Note'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('resolved_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'issue', ['Issue'])

        # Adding model 'IssueComment'
        db.create_table(u'issue_issuecomment', (
            (u'note_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['issue.Note'], unique=True, primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['issue.Issue'])),
            ('comment_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'issue', ['IssueComment'])

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
            ('action_order', self.gf('django.db.models.fields.IntegerField')()),
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
        # Deleting model 'Note'
        db.delete_table(u'issue_note')

        # Deleting model 'Issue'
        db.delete_table(u'issue_issue')

        # Deleting model 'IssueComment'
        db.delete_table(u'issue_issuecomment')

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
            'Meta': {'object_name': 'Issue', '_ormbases': [u'issue.Note']},
            u'note_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['issue.Note']", 'unique': 'True', 'primary_key': 'True'}),
            'resolved_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'issue.issuecomment': {
            'Meta': {'object_name': 'IssueComment', '_ormbases': [u'issue.Note']},
            'comment_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['issue.Issue']"}),
            u'note_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['issue.Note']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'issue.note': {
            'Meta': {'object_name': 'Note'},
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'details': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        u'issue.responder': {
            'Meta': {'object_name': 'Responder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'watch_pattern': ('regex_field.fields.RegexField', [], {'max_length': '128'})
        },
        u'issue.responderaction': {
            'Meta': {'object_name': 'ResponderAction'},
            'action_order': ('django.db.models.fields.IntegerField', [], {}),
            'function_kwargs': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': u"orm['issue.Responder']"}),
            'target_function': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['issue']