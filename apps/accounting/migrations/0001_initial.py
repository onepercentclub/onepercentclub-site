# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BankTransaction'
        db.create_table(u'accounting_banktransaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender_account', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('interest_date', self.gf('django.db.models.fields.DateField')()),
            ('credit_debit', self.gf('django.db.models.fields.CharField')(max_length=1, db_index=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('counter_account', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('counter_name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('book_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('book_code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('filler', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('description1', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('description2', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('description3', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('description4', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('description5', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('description6', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('end_to_end_id', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('id_recipient', self.gf('django.db.models.fields.CharField')(max_length=35)),
            ('mandate_id', self.gf('django.db.models.fields.CharField')(max_length=35)),
        ))
        db.send_create_signal(u'accounting', ['BankTransaction'])

        # Adding model 'DocdataPayout'
        db.create_table(u'accounting_docdatapayout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('period_id', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2, blank=True)),
        ))
        db.send_create_signal(u'accounting', ['DocdataPayout'])

        # Adding model 'DocdataPayment'
        db.create_table(u'accounting_docdatapayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('merchant_reference', self.gf('django.db.models.fields.CharField')(unique=True, max_length=35)),
            ('triple_deal_reference', self.gf('django.db.models.fields.PositiveIntegerField')(unique=True)),
            ('payment_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('amount_registered', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency_amount_registered', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('amount_collected', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency_amount_collected', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('tpcd', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2, blank=True)),
            ('currency_tpcd', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('tpci', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency_tpci', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('docdata_fee', self.gf('django.db.models.fields.DecimalField')(max_digits=14, decimal_places=2)),
            ('currency_docdata_fee', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal(u'accounting', ['DocdataPayment'])


    def backwards(self, orm):
        # Deleting model 'BankTransaction'
        db.delete_table(u'accounting_banktransaction')

        # Deleting model 'DocdataPayout'
        db.delete_table(u'accounting_docdatapayout')

        # Deleting model 'DocdataPayment'
        db.delete_table(u'accounting_docdatapayment')


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
            'Meta': {'object_name': 'DocdataPayment'},
            'amount_collected': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'amount_registered': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'currency_amount_collected': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_amount_registered': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_docdata_fee': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'currency_tpcd': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'currency_tpci': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'docdata_fee': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_reference': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '35'}),
            'payment_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'tpcd': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2', 'blank': 'True'}),
            'tpci': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'triple_deal_reference': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True'})
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