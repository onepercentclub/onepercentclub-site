# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table(u'geo_region', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
        ))
        db.send_create_signal(u'geo', ['Region'])

        # Adding model 'SubRegion'
        db.create_table(u'geo_subregion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Region'])),
        ))
        db.send_create_signal(u'geo', ['SubRegion'])

        # Adding model 'Country'
        db.create_table(u'geo_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('subregion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.SubRegion'])),
            ('alpha2_code', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('alpha3_code', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('oda_recipient', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'geo', ['Country'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table(u'geo_region')

        # Deleting model 'SubRegion'
        db.delete_table(u'geo_subregion')

        # Deleting model 'Country'
        db.delete_table(u'geo_country')


    models = {
        u'geo.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alpha2_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alpha3_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'oda_recipient': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.SubRegion']"})
        },
        u'geo.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        u'geo.subregion': {
            'Meta': {'ordering': "['name']", 'object_name': 'SubRegion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Region']"})
        }
    }

    complete_apps = ['geo']