# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Payout'
        db.create_table(u'payouts_payout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('planned', self.gf('django.db.models.fields.DateField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('sender_account_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_iban', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_bic', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('receiver_account_country', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('invoice_reference', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description_line1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line3', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
            ('description_line4', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True)),
        ))
        db.send_create_signal(u'payouts', ['Payout'])

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
        # Deleting model 'Payout'
        db.delete_table(u'payouts_payout')

        # Deleting model 'BankMutationLine'
        db.delete_table(u'payouts_bankmutationline')

        # Deleting model 'BankMutation'
        db.delete_table(u'payouts_bankmutation')


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
        u'payouts.payout': {
            'Meta': {'object_name': 'Payout'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'description_line1': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line3': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description_line4': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_reference': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'planned': ('django.db.models.fields.DateField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'receiver_account_bic': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'receiver_account_iban': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'receiver_account_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sender_account_number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'projects.partnerorganization': {
            'Meta': {'object_name': 'PartnerOrganization'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'projects.project': {
            'Meta': {'ordering': "['title']", 'object_name': 'Project'},
            'coach': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'team_member'", 'null': 'True', 'to': u"orm['accounts.BlueBottleUser']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['accounts.BlueBottleUser']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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