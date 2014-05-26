# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BankTransactionCategory'
        db.create_table(u'accounting_banktransactioncategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'accounting', ['BankTransactionCategory'])

        # Adding field 'BankTransaction.category'
        db.add_column(u'accounting_banktransaction', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounting.BankTransactionCategory'], null=True),
                      keep_default=False)

        # Adding field 'BankTransaction.payout'
        db.add_column(u'accounting_banktransaction', 'payout',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payouts.Payout'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'BankTransactionCategory'
        db.delete_table(u'accounting_banktransactioncategory')

        # Deleting field 'BankTransaction.category'
        db.delete_column(u'accounting_banktransaction', 'category_id')

        # Deleting field 'BankTransaction.payout'
        db.delete_column(u'accounting_banktransaction', 'payout_id')


    models = {
        u'accounting.banktransaction': {
            'Meta': {'object_name': 'BankTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
            'book_code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'book_date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounting.BankTransactionCategory']", 'null': 'True'}),
            'counter_account': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'counter_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'credit_debit': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'description1': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'description2': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'description3': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'description4': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'description5': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'description6': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'end_to_end_id': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'filler': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_recipient': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'interest_date': ('django.db.models.fields.DateField', [], {}),
            'mandate_id': ('django.db.models.fields.CharField', [], {'max_length': '35', 'blank': 'True'}),
            'payout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payouts.Payout']", 'null': 'True'}),
            'sender_account': ('django.db.models.fields.CharField', [], {'max_length': '35'})
        },
        u'accounting.banktransactioncategory': {
            'Meta': {'object_name': 'BankTransactionCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'bb_accounts.timeavailable': {
            'Meta': {'ordering': "['type']", 'object_name': 'TimeAvailable'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'bb_projects.projectphase': {
            'Meta': {'ordering': "['sequence']", 'object_name': 'ProjectPhase'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'viewable': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'bb_projects.projecttheme': {
            'Meta': {'ordering': "['name']", 'object_name': 'ProjectTheme'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'name_nl': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'geo.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alpha2_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alpha3_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'oda_recipient': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.SubRegion']"})
        },
        u'geo.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'geo.subregion': {
            'Meta': {'ordering': "['name']", 'object_name': 'SubRegion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Region']"})
        },
        u'members.member': {
            'Meta': {'object_name': 'Member'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '265', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'}),
            'facebook': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'newsletter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'primary_language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'share_money': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'share_time_knowledge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'skypename': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'time_available': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bb_accounts.TimeAvailable']", 'null': 'True', 'blank': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'person'", 'max_length': '25'}),
            'username': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'why': ('django.db.models.fields.TextField', [], {'max_length': '265', 'blank': 'True'})
        },
        u'organizations.organization': {
            'Meta': {'ordering': "['name']", 'object_name': 'Organization'},
            'account_bank_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_bank_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_bank_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'account_bank_country'", 'null': 'True', 'to': u"orm['geo.Country']"}),
            'account_bank_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_bank_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'account_bic': ('django_iban.fields.SWIFTBICField', [], {'max_length': '11', 'blank': 'True'}),
            'account_holder_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_holder_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_holder_country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'account_holder_country'", 'null': 'True', 'to': u"orm['geo.Country']"}),
            'account_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_holder_postal_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'account_iban': ('django_iban.fields.IBANField', [], {'max_length': '34', 'blank': 'True'}),
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_other': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'country'", 'null': 'True', 'to': u"orm['geo.Country']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'facebook': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'partner_organizations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'registration': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'skype': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'payouts.payout': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Payout'},
            'amount_payable': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'amount_raised': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description_line1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization_fee': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payout_rule': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'planned': ('django.db.models.fields.DateField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'receiver_account_bic': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'receiver_account_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'receiver_account_iban': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'receiver_account_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'sender_account_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'projects.partnerorganization': {
            'Meta': {'object_name': 'PartnerOrganization'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'projects.project': {
            'Meta': {'ordering': "['title']", 'object_name': 'Project'},
            'allow_overfunding': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'amount_asked': ('apps.projects.fields.MoneyField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'amount_donated': ('apps.projects.fields.MoneyField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'amount_needed': ('apps.projects.fields.MoneyField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'campaign_ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'campaign_funded': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'campaign_started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'date_submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'effects': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'favorite': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'for_who': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'future': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'blank': 'True'}),
            'is_campaign': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utils.Language']", 'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '21', 'decimal_places': '18', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '21', 'decimal_places': '18', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organization'", 'null': 'True', 'to': u"orm['organizations.Organization']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['members.Member']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'pitch': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'popularity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reach': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bb_projects.ProjectPhase']"}),
            'story': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bb_projects.ProjectTheme']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'video_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        },
        u'utils.language': {
            'Meta': {'ordering': "['language_name']", 'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounting']