# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Statistic'
        db.create_table(u'statistics_statistic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lives_changed', self.gf('django.db.models.fields.IntegerField')()),
            ('projects', self.gf('django.db.models.fields.IntegerField')()),
            ('countries', self.gf('django.db.models.fields.IntegerField')()),
            ('hours_spent', self.gf('django.db.models.fields.IntegerField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal(u'statistics', ['Statistic'])


    def backwards(self, orm):
        # Deleting model 'Statistic'
        db.delete_table(u'statistics_statistic')


    models = {
        u'statistics.statistic': {
            'Meta': {'object_name': 'Statistic'},
            'countries': ('django.db.models.fields.IntegerField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'hours_spent': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lives_changed': ('django.db.models.fields.IntegerField', [], {}),
            'projects': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['statistics']