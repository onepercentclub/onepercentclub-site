# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Redirect'
        db.create_table('django_redirect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('old_path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200, db_index=True)),
            ('new_path', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('regular_expression', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fallback_redirect', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nr_times_visited', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'redirects', ['Redirect'])


    def backwards(self, orm):
        # Deleting model 'Redirect'
        db.delete_table('django_redirect')


    models = {
        u'redirects.redirect': {
            'Meta': {'ordering': "('fallback_redirect', 'regular_expression', 'old_path')", 'object_name': 'Redirect', 'db_table': "'django_redirect'"},
            'fallback_redirect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'nr_times_visited': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'old_path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'regular_expression': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['redirects']