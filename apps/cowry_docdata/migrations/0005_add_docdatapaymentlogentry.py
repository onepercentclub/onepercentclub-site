# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocDataPaymentLogEntry'
        db.create_table(u'cowry_docdata_docdatapaymentlogentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('docdata_payment_order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_entries', to=orm['cowry_docdata.DocDataPaymentOrder'])),
        ))
        db.send_create_signal(u'cowry_docdata', ['DocDataPaymentLogEntry'])

        # Deleting field 'DocDataPayment.docdata_payment_method'
        db.delete_column(u'cowry_docdata_docdatapayment', 'docdata_payment_method')

        # Adding field 'DocDataPayment.payment_method'
        db.add_column(u'cowry_docdata_docdatapayment', 'payment_method',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'DocDataPaymentLogEntry'
        db.delete_table(u'cowry_docdata_docdatapaymentlogentry')

        # Adding field 'DocDataPayment.docdata_payment_method'
        db.add_column(u'cowry_docdata_docdatapayment', 'docdata_payment_method',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True),
                      keep_default=False)

        # Deleting field 'DocDataPayment.payment_method'
        db.delete_column(u'cowry_docdata_docdatapayment', 'payment_method')


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
            'currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
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
            'docdata_payment_order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'docdata_payments'", 'to': u"orm['cowry_docdata.DocDataPaymentOrder']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cowry_docdata.docdatapayment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'cowry_docdata.docdatapaymentlogentry': {
            'Meta': {'object_name': 'DocDataPaymentLogEntry'},
            'docdata_payment_order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'to': u"orm['cowry_docdata.DocDataPaymentOrder']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        u'cowry_docdata.docdatapaymentorder': {
            'Meta': {'object_name': 'DocDataPaymentOrder', '_ormbases': [u'cowry.Payment']},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'customer_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '254'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'merchant_order_reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'payment_order_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
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