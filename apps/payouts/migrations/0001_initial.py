# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Payout'
        db.create_table(u'payouts_payout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice_reference', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('completed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('planned', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('payout_rule', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('amount_raised', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('organization_fee', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('amount_payable', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('sender_account_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_number', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('receiver_account_iban', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('receiver_account_bic', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('receiver_account_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_country', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('description_line1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal(u'payouts', ['Payout'])

        # Adding model 'PayoutLog'
        db.create_table(u'payouts_payoutlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('old_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('new_status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('payout', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_set', to=orm['payouts.Payout'])),
        ))
        db.send_create_signal(u'payouts', ['PayoutLog'])

        # Adding model 'OrganizationPayout'
        db.create_table(u'payouts_organizationpayout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice_reference', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('completed', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('planned', self.gf('django.db.models.fields.DateField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('organization_fee_excl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('organization_fee_vat', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('organization_fee_incl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('psp_fee_excl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('psp_fee_vat', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('psp_fee_incl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('other_costs_excl', self.gf('apps.payouts.fields.MoneyField')(default='0.00', max_digits=12, decimal_places=2)),
            ('other_costs_vat', self.gf('apps.payouts.fields.MoneyField')(default='0.00', max_digits=12, decimal_places=2)),
            ('other_costs_incl', self.gf('apps.payouts.fields.MoneyField')(default='0.00', max_digits=12, decimal_places=2)),
            ('payable_amount_excl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('payable_amount_vat', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
            ('payable_amount_incl', self.gf('apps.payouts.fields.MoneyField')(max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal(u'payouts', ['OrganizationPayout'])

        # Adding unique constraint on 'OrganizationPayout', fields ['start_date', 'end_date']
        db.create_unique(u'payouts_organizationpayout', ['start_date', 'end_date'])

        # Adding model 'OrganizationPayoutLog'
        db.create_table(u'payouts_organizationpayoutlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('old_status', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('new_status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('payout', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_set', to=orm['payouts.OrganizationPayout'])),
        ))
        db.send_create_signal(u'payouts', ['OrganizationPayoutLog'])

        # Adding model 'BankMutationLine'
        db.create_table(u'payouts_bankmutationline', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('bank_mutation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payouts.BankMutation'])),
            ('issuer_account_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('dc', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=2)),
            ('account_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('account_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('transaction_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('invoice_reference', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description_line1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('payout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payouts.Payout'], null=True)),
        ))
        db.send_create_signal(u'payouts', ['BankMutationLine'])

        # Adding model 'BankMutation'
        db.create_table(u'payouts_bankmutation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('mut_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('mutations', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'payouts', ['BankMutation'])


    def backwards(self, orm):
        # Removing unique constraint on 'OrganizationPayout', fields ['start_date', 'end_date']
        db.delete_unique(u'payouts_organizationpayout', ['start_date', 'end_date'])

        # Deleting model 'Payout'
        db.delete_table(u'payouts_payout')

        # Deleting model 'PayoutLog'
        db.delete_table(u'payouts_payoutlog')

        # Deleting model 'OrganizationPayout'
        db.delete_table(u'payouts_organizationpayout')

        # Deleting model 'OrganizationPayoutLog'
        db.delete_table(u'payouts_organizationpayoutlog')

        # Deleting model 'BankMutationLine'
        db.delete_table(u'payouts_bankmutationline')

        # Deleting model 'BankMutation'
        db.delete_table(u'payouts_bankmutation')


    models = {
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
        u'bb_projects.projectphase': {
            'Meta': {'ordering': "['sequence']", 'object_name': 'ProjectPhase'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
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
            'availability': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
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
            'twitter': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'person'", 'max_length': '25'}),
            'username': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'why': ('django.db.models.fields.TextField', [], {'max_length': '265', 'blank': 'True'})
        },
        u'payouts.bankmutation': {
            'Meta': {'object_name': 'BankMutation'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mut_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'mutations': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'payouts.bankmutationline': {
            'Meta': {'object_name': 'BankMutationLine'},
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'bank_mutation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payouts.BankMutation']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'dc': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'description_line1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'issuer_account_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'payout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payouts.Payout']", 'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'payouts.organizationpayout': {
            'Meta': {'ordering': "['start_date']", 'unique_together': "(('start_date', 'end_date'),)", 'object_name': 'OrganizationPayout'},
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization_fee_excl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'organization_fee_incl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'organization_fee_vat': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_excl': ('apps.payouts.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_incl': ('apps.payouts.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_vat': ('apps.payouts.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_excl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_incl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_vat': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'planned': ('django.db.models.fields.DateField', [], {}),
            'psp_fee_excl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'psp_fee_incl': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'psp_fee_vat': ('apps.payouts.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'payouts.organizationpayoutlog': {
            'Meta': {'ordering': "['-date']", 'object_name': 'OrganizationPayoutLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'old_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'payout': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_set'", 'to': u"orm['payouts.OrganizationPayout']"})
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
        u'payouts.payoutlog': {
            'Meta': {'ordering': "['-date']", 'object_name': 'PayoutLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'old_status': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'payout': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_set'", 'to': u"orm['payouts.Payout']"})
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
            'coach': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'team_member'", 'null': 'True', 'to': u"orm['members.Member']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['geo.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'favorite': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'blank': 'True'}),
            'is_campaign': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '21', 'decimal_places': '18', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '21', 'decimal_places': '18', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['members.Member']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pitch': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'popularity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reach': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bb_projects.ProjectPhase']"}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bb_projects.ProjectTheme']", 'null': 'True'}),
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
        }
    }

    complete_apps = ['payouts']