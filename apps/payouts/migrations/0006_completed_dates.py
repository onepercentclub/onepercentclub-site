# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    def forwards(self, orm):
        """ Set closed days for past payouts. """
        # Dictionary with known id -> completed date pairs
        completed_dates = {
            # A colourful future for disadvantaged children in Nicaragua
            1824: datetime.date(2013, 12, 31),
            # Bamboe voor de Ambachtsschool
            1543: datetime.date(2013, 9, 30),
            # Bandung Barat project
            1415: datetime.date(2013, 12, 18),
            # Betere locatie, meer kansen!
            1625: datetime.date(2013, 9, 30),
            # Bouwen voor boeken!
            1482: datetime.date(2013, 10, 15),
            # Clean Lighting and Phone Recharging Initiative - Cameroon
            1634: datetime.date(2013, 9, 30),
            # Computercursus voor dove scholieren!
            1534: datetime.date(2013, 12, 3),
            # Empower the Women and Youth of Rakhine State (Myanmar)
            1849: datetime.date(2013, 12, 17),
            # Future Stars Project
            1376: datetime.date(2013, 12, 2),
            # GIVE A CUSHION TOO!
            1660: datetime.date(2013, 9, 27),
            # Goodget - Improving Daily Life
            1429: datetime.date(2013, 12, 18),
            # Heerlijk Helder Water Pompen
            1614: datetime.date(2013, 10, 15),
            # Hope From The Farm
            1380: datetime.date(2013, 12, 31),
            # Independence for HIV-orphans!
            1628: datetime.date(2013, 9, 30),
            # Two water enterprises Northern Cambodia
            1495: datetime.date(2013, 12, 18),
            # Watertank voor schoolkinderen
            1350: datetime.date(2013, 12, 18),
            # a school + building skills for the Sherpa people in Nepal
            1804: datetime.date(2013, 12, 3),
            # livelihood and women empowerment program (LWEP)
            1607: datetime.date(2013, 12, 31),
        }

        # The above are project id's
        payouts = orm.Payout.objects.filter(project_id__in=completed_dates.keys()).distinct()

        for payout in payouts:
            payout.completed = completed_dates[payout.project.id]
            payout.save()

    def backwards(self, orm):
        """ Do nothing; all generated fields are nonexistent anyways. """
        pass

    models = {
        u'accounts.bluebottleuser': {
            'Meta': {'object_name': 'BlueBottleUser'},
            'about': ('django.db.models.fields.TextField', [], {'max_length': '265', 'blank': 'True'}),
            'availability': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'available_time': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'birthdate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'contribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254', 'db_index': 'True'}),
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
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'person'", 'max_length': '25'}),
            'username': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'why': ('django.db.models.fields.TextField', [], {'max_length': '265', 'blank': 'True'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        u'payouts.payout': {
            'Meta': {'object_name': 'Payout'},
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
            'coach': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'team_member'", 'null': 'True', 'to': u"orm['accounts.BlueBottleUser']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_campaign': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['accounts.BlueBottleUser']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'payout_rule': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'popularity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
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
    symmetrical = True
