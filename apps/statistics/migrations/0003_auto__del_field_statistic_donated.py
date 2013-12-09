# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Statistic.donated'
        db.delete_column(u'statistics_statistic', 'donated')


    def backwards(self, orm):
        # Adding field 'Statistic.donated'
        db.add_column(u'statistics_statistic', 'donated',
                      self.gf('django.db.models.fields.IntegerField')(default=987123),
                      keep_default=False)


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