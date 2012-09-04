# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table('geo_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
        ))
        db.send_create_signal('geo', ['Region'])

        # Adding model 'SubRegion'
        db.create_table('geo_subregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Region'])),
        ))
        db.send_create_signal('geo', ['SubRegion'])

        # Adding model 'Country'
        db.create_table('geo_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('numeric_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('subregion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.SubRegion'])),
            ('alpha2_code', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('alpha3_code', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('oda_recipient', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('geo', ['Country'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table('geo_region')

        # Deleting model 'SubRegion'
        db.delete_table('geo_subregion')

        # Deleting model 'Country'
        db.delete_table('geo_country')


    models = {
        'geo.country': {
            'Meta': {'object_name': 'Country'},
            'alpha2_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alpha3_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'oda_recipient': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.SubRegion']"})
        },
        'geo.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        'geo.subregion': {
            'Meta': {'object_name': 'SubRegion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Region']"})
        }
    }

    complete_apps = ['geo']