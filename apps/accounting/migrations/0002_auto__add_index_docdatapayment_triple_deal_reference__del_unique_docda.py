# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DocdataPayment', fields ['merchant_reference']
        db.delete_unique(u'accounting_docdatapayment', ['merchant_reference'])

        # Removing unique constraint on 'DocdataPayment', fields ['triple_deal_reference']
        db.delete_unique(u'accounting_docdatapayment', ['triple_deal_reference'])

        # Adding index on 'DocdataPayment', fields ['triple_deal_reference']
        db.create_index(u'accounting_docdatapayment', ['triple_deal_reference'])


        # Changing field 'DocdataPayment.tpci'
        db.alter_column(u'accounting_docdatapayment', 'tpci', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))
        # Adding index on 'DocdataPayment', fields ['merchant_reference']
        db.create_index(u'accounting_docdatapayment', ['merchant_reference'])

        # Adding index on 'DocdataPayment', fields ['payment_type']
        db.create_index(u'accounting_docdatapayment', ['payment_type'])

        # Adding unique constraint on 'DocdataPayment', fields ['triple_deal_reference', 'merchant_reference', 'payment_type']
        db.create_unique(u'accounting_docdatapayment', ['triple_deal_reference', 'merchant_reference', 'payment_type'])


    def backwards(self, orm):
        # Removing unique constraint on 'DocdataPayment', fields ['triple_deal_reference', 'merchant_reference', 'payment_type']
        db.delete_unique(u'accounting_docdatapayment', ['triple_deal_reference', 'merchant_reference', 'payment_type'])

        # Removing index on 'DocdataPayment', fields ['payment_type']
        db.delete_index(u'accounting_docdatapayment', ['payment_type'])

        # Removing index on 'DocdataPayment', fields ['merchant_reference']
        db.delete_index(u'accounting_docdatapayment', ['merchant_reference'])

        # Removing index on 'DocdataPayment', fields ['triple_deal_reference']
        db.delete_index(u'accounting_docdatapayment', ['triple_deal_reference'])

        # Adding unique constraint on 'DocdataPayment', fields ['triple_deal_reference']
        db.create_unique(u'accounting_docdatapayment', ['triple_deal_reference'])


        # Changing field 'DocdataPayment.tpci'
        db.alter_column(u'accounting_docdatapayment', 'tpci', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=14, decimal_places=2))
        # Adding unique constraint on 'DocdataPayment', fields ['merchant_reference']
        db.create_unique(u'accounting_docdatapayment', ['merchant_reference'])


    models = {
        u'accounting.banktransaction': {
            'Meta': {'object_name': 'BankTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'book_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'book_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'counter_account': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'counter_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'credit_debit': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'description1': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'description2': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'description3': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'description4': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'description5': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'description6': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'end_to_end_id': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'filler': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_recipient': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'interest_date': ('django.db.models.fields.DateField', [], {}),
            'mandate_id': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'sender_account': ('django.db.models.fields.CharField', [], {'max_length': '35'})
        },
        u'accounting.docdatapayment': {
            'Meta': {'unique_together': "(('merchant_reference', 'triple_deal_reference', 'payment_type'),)", 'object_name': 'DocdataPayment'},
            'amount_collected': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'amount_registered': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'currency_amount_collected': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_amount_registered': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_docdata_fee': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_tpcd': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'currency_tpci': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'docdata_fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_reference': ('django.db.models.fields.CharField', [], {'max_length': '35', 'db_index': 'True'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'tpcd': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tpci': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'triple_deal_reference': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'accounting.docdatapayout': {
            'Meta': {'object_name': 'DocdataPayout'},
            'end_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_id': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'})
        }
    }

    complete_apps = ['accounting']