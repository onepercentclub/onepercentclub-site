# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    depends_on = (
        ('payouts', '0001_initial'),
        ('bb_payouts', '0001_initial')
    )

    def forwards(self, orm):
        # Delete initial (empty) tables for new payout modeling.
        db.delete_table('bb_payouts_projectpayoutlog')
        db.delete_table('bb_payouts_organizationpayoutlog')
        db.delete_table('payouts_projectpayout')

        # Rename old table names to new scheme
        db.rename_table('payouts_payout', 'payouts_projectpayout')
        db.rename_table('payouts_payoutlog', 'bb_payouts_projectpayoutlog')
        db.rename_table('payouts_organizationpayoutlog', 'bb_payouts_organizationpayoutlog')
        db.rename_column('bb_payouts_projectpayoutlog', 'date', 'created')
        db.rename_column('bb_payouts_organizationpayoutlog', 'date', 'created')

    def backwards(self, orm):
        db.rename_column('bb_payouts_projectpayoutlog', 'created', 'date')
        db.rename_column('bb_payouts_organizationpayoutlog', 'created', 'date')
        db.rename_table('payouts_projectpayout', 'payouts_payout')
        db.rename_table('bb_payouts_projectpayoutlog', 'payouts_payoutlog')
        db.rename_table('bb_payouts_organizationpayoutlog', 'payouts_organizationpayoutlog')

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
            'owner_editable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        u'fund.donation': {
            'Meta': {'object_name': 'Donation'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'one_off'", 'max_length': '20', 'db_index': 'True'}),
            'fundraiser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_donations'", 'null': 'True', 'to': u"orm['fundraisers.FundRaiser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'donations'", 'null': 'True', 'to': u"orm['fund.Order']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_donations'", 'to': u"orm['projects.Project']"}),
            'ready': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['members.Member']", 'null': 'True', 'blank': 'True'}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vouchers.Voucher']", 'null': 'True', 'blank': 'True'})
        },
        u'fund.order': {
            'Meta': {'ordering': "('-updated',)", 'object_name': 'Order'},
            'closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'}),
            'recurring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'current'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_orders'", 'null': 'True', 'to': u"orm['members.Member']"})
        },
        u'fundraisers.fundraiser': {
            'Meta': {'object_name': 'FundRaiser'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': "'10'"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['members.Member']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'video_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
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
            'available_time': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'disable_token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'}),
            'facebook': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
        u'payouts.organizationpayout': {
            'Meta': {'ordering': "['start_date']", 'unique_together': "(('start_date', 'end_date'),)", 'object_name': 'OrganizationPayout'},
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization_fee_excl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'organization_fee_incl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'organization_fee_vat': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_excl': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_incl': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'other_costs_vat': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': "'0.00'", 'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_excl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_incl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'payable_amount_vat': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'planned': ('django.db.models.fields.DateField', [], {}),
            'psp_fee_excl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'psp_fee_incl': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'psp_fee_vat': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'payouts.projectpayout': {
            'Meta': {'ordering': "['-created']", 'object_name': 'ProjectPayout'},
            'amount_payable': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'amount_raised': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'completed': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description_line1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'organization_fee': ('bluebottle.bb_projects.fields.MoneyField', [], {'max_digits': '12', 'decimal_places': '2'}),
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
            'submitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
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
            'amount_asked': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': '0', 'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'amount_donated': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'amount_needed': ('bluebottle.bb_projects.fields.MoneyField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
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
            'mchanga_account': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organization'", 'null': 'True', 'to': u"orm['organizations.Organization']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['members.Member']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'pitch': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'popularity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reach': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'skip_monthly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        },
        u'vouchers.voucher': {
            'Meta': {'object_name': 'Voucher'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vouchers'", 'null': 'True', 'to': u"orm['fund.Order']"}),
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receiver'", 'null': 'True', 'to': u"orm['members.Member']"}),
            'receiver_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'receiver_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sender'", 'null': 'True', 'to': u"orm['members.Member']"}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        }
    }

    complete_apps = ['payouts', 'fund']
    symmetrical = True
