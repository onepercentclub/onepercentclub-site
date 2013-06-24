# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocDataPaymentOrder'
        db.create_table(u'cowry_docdata_docdatapaymentorder', (
            (u'payment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cowry.Payment'], unique=True, primary_key=True)),
            ('payment_order_key', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('merchant_order_reference', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('customer_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('email', self.gf('django.db.models.fields.EmailField')(default='', max_length=254)),
            ('first_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(default='', max_length=20)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en', max_length=2)),
        ))
        db.send_create_signal(u'cowry_docdata', ['DocDataPaymentOrder'])

        # Adding model 'DocDataPayment'
        db.create_table(u'cowry_docdata_docdatapayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_cowry_docdata.docdatapayment_set', null=True, to=orm['contenttypes.ContentType'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='NEW', max_length=25)),
            ('docdata_payment_order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cowry_docdata.DocDataPaymentOrder'])),
            ('payment_id', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('docdata_payment_method', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal(u'cowry_docdata', ['DocDataPayment'])

        # Adding model 'DocDataWebDirectDirectDebit'
        db.create_table(u'cowry_docdata_docdatawebdirectdirectdebit', (
            (u'docdatapayment_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cowry_docdata.DocDataPayment'], unique=True, primary_key=True)),
            ('bank_account_number', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
            ('bank_account_name', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('bank_account_city', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal(u'cowry_docdata', ['DocDataWebDirectDirectDebit'])


    def backwards(self, orm):
        # Deleting model 'DocDataPaymentOrder'
        db.delete_table(u'cowry_docdata_docdatapaymentorder')

        # Deleting model 'DocDataPayment'
        db.delete_table(u'cowry_docdata_docdatapayment')

        # Deleting model 'DocDataWebDirectDirectDebit'
        db.delete_table(u'cowry_docdata_docdatawebdirectdirectdebit')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cowry.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3', 'blank': 'True'}),
            'fee': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_method_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'payment_submethod_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cowry.payment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '15', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'cowry_docdata.docdatapayment': {
            'Meta': {'object_name': 'DocDataPayment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'docdata_payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'docdata_payment_order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cowry_docdata.DocDataPaymentOrder']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cowry_docdata.docdatapayment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '25'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'cowry_docdata.docdatapaymentorder': {
            'Meta': {'object_name': 'DocDataPaymentOrder', '_ormbases': [u'cowry.Payment']},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'customer_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '254'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'merchant_order_reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'payment_order_key': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'payment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cowry.Payment']", 'unique': 'True', 'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'})
        },
        u'cowry_docdata.docdatawebdirectdirectdebit': {
            'Meta': {'object_name': 'DocDataWebDirectDirectDebit', '_ormbases': [u'cowry_docdata.DocDataPayment']},
            'bank_account_city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'bank_account_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'bank_account_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            u'docdatapayment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cowry_docdata.DocDataPayment']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['cowry_docdata']