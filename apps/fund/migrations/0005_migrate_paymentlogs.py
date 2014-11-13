# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from bluebottle.utils.model_dispatcher import get_model_mapping

MODEL_MAP = get_model_mapping()

class Migration(DataMigration):

    depends_on = (
        ('bluebottle.payments_logger', '0001_initial'),
        ('bluebottle.payments_docdata', '0002_auto__add_field_docdatapayment_customer_id__add_field_docdatapayment_e'),
    )

    def forwards(self, orm):
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        count = 0
        total = orm['cowry_docdata.DocDataPaymentLogEntry'].objects.count()
        for i, log_entry_model in enumerate(orm['cowry_docdata.DocDataPaymentLogEntry'].objects.all()):
            if not i % 50:
                print "Processing DocdataPaymentLogEntry {0} of {1}".format(i, total)

            # Fetch DocDataPaymentOrder
            old_docdata_payment_order = log_entry_model.docdata_payment_order

            # Fetch corresponding DocdataPayment
            try:
                new_docdata_payment = orm['payments_docdata.DocdataPayment'].objects.get(payment_cluster_id=old_docdata_payment_order.merchant_order_reference)
            except orm['payments_docdata.DocdataPayment'].DoesNotExist:
                count +=1
                msg = "No new DocdataPayment object found for the old DocdataPaymentOrder object. DocdataPaymentOrder ID: {0} DocDataPaymentLogEntry ID: {1}".format(old_docdata_payment_order.id, log_entry_model.id)
                print msg
                continue

            # Create new PaymentLogEntry using the old DocDataPaymentLogEntry data
            payment_log_entry = orm['payments_logger.PaymentLogEntry'].objects.create(
                message=log_entry_model.message,
                level=log_entry_model.level,
                timestamp=log_entry_model.timestamp,
                payment=new_docdata_payment
            )

            payment_log_entry.save()
            if not i % 50:
                print "PaymentLogEntry {0} created".format(i)
        print "PaymentLogEntries without DocdataPayment: {0}".format(count)
        
    def backwards(self, orm):
        orm['payments_logger.PaymentLogEntry'].objects.all().delete()

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
        u'cowry.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3'}),
            'fee': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['fund.Order']"}),
            'payment_method_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'payment_submethod_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cowry.payment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '15', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'cowry_docdata.docdatapayment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocDataPayment'},
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
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'DocDataPaymentLogEntry'},
            'docdata_payment_order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_entries'", 'to': u"orm['cowry_docdata.DocDataPaymentOrder']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'cowry_docdata.docdatapaymentorder': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocDataPaymentOrder', '_ormbases': [u'cowry.Payment']},
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
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocDataWebDirectDirectDebit', '_ormbases': [u'cowry_docdata.DocDataPayment']},
            'account_city': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'bic': ('django_iban.fields.SWIFTBICField', [], {'max_length': '11'}),
            u'docdatapayment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cowry_docdata.DocDataPayment']", 'unique': 'True', 'primary_key': 'True'}),
            'iban': ('django_iban.fields.IBANField', [], {'max_length': '34'})
        },
        u'fund.donation': {
            'Meta': {'object_name': MODEL_MAP['donation']['class']},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'one_off'", 'max_length': '20', 'db_index': 'True'}),
            'fundraiser': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_donations'", 'null': 'True', 'to': "orm['{0}']".format(MODEL_MAP['fundraiser']['model'])}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'donations'", 'null': 'True', 'to': u"orm['fund.Order']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'old_donations'", 'to': "orm['{0}']".format(MODEL_MAP['project']['model'])}),
            'ready': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{0}']".format(MODEL_MAP['user']['model']), 'null': 'True', 'blank': 'True'}),
            'voucher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['vouchers.Voucher']", 'null': 'True', 'blank': 'True'})
        },
        u'fund.order': {
            'Meta': {'ordering': "('-updated',)", 'object_name': MODEL_MAP['order']['class']},
            'closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'}),
            'recurring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'current'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_orders'", 'null': 'True', 'to': "orm['{0}']".format(MODEL_MAP['user']['model'])})
        },
        u'fund.recurringdirectdebitpayment': {
            'Meta': {'object_name': 'RecurringDirectDebitPayment'},
            'account': ('apps.fund.fields.DutchBankAccountField', [], {'max_length': '10'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'bic': ('django_iban.fields.SWIFTBICField', [], {'default': "''", 'max_length': '11', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': '3'}),
            'iban': ('django_iban.fields.IBANField', [], {'default': "''", 'max_length': '34', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manually_process': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['{0}']".format(MODEL_MAP['user']['model']), 'unique': 'True'})
        },
        MODEL_MAP['fundraiser']['model_lower']: {
            'Meta': {'object_name': MODEL_MAP['fundraiser']['class']},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'default': "'EUR'", 'max_length': "'10'"}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{0}']".format(MODEL_MAP['user']['model'])}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{0}']".format(MODEL_MAP['project']['model'])}),
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
        MODEL_MAP['user']['model_lower']: {
            'Meta': {'object_name': MODEL_MAP['user']['class']},
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
        MODEL_MAP['order']['model_lower']: {
            'Meta': {'object_name': MODEL_MAP['order']['class']},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'confirmed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'created'", 'max_length': '50'}),
            'total': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{0}']".format(MODEL_MAP['user']['model']), 'null': 'True', 'blank': 'True'})
        },
        MODEL_MAP['organization']['model_lower']: {
            'Meta': {'ordering': "['name']", 'object_name': MODEL_MAP['organization']['class']},
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
        u'payments.orderpayment': {
            'Meta': {'object_name': 'OrderPayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '2'}),
            'authorization_action': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payments.OrderPaymentAction']", 'unique': 'True', 'null': 'True'}),
            'closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'integration_data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'max_length': '5000', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_payments'", 'to': "orm['{0}']".format(MODEL_MAP['order']['model'])}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'status': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'created'", 'max_length': '50'}),
            'transaction_fee': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '16', 'decimal_places': '2'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{0}']".format(MODEL_MAP['user']['model']), 'null': 'True', 'blank': 'True'})
        },
        u'payments.orderpaymentaction': {
            'Meta': {'object_name': 'OrderPaymentAction'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'payload': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'})
        },
        u'payments.payment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'Payment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_payment': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payments.OrderPayment']", 'unique': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_payments.payment_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'status': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'started'", 'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'payments.transaction': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'Transaction'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.Payment']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_payments.transaction_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'payments_docdata.docdatadirectdebittransaction': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocDataDirectDebitTransaction', '_ormbases': [u'payments.Transaction']},
            'account_city': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'bic': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            'iban': ('django.db.models.fields.CharField', [], {'max_length': '35'}),
            u'transaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payments.Transaction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'payments_docdata.docdatapayment': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataPayment', '_ormbases': [u'payments.Payment']},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'customer_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'default_pm': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '254'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'ideal_issuer_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'merchant_order_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'payment_cluster_id': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '200'}),
            'payment_cluster_key': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '200'}),
            u'payment_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payments.Payment']", 'unique': 'True', 'primary_key': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'total_acquirer_approved': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_acquirer_pending': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_captured': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_charged_back': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_gross_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'total_refunded': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_registered': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'}),
            'total_shopper_pending': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '15', 'decimal_places': '2'})
        },
        u'payments_docdata.docdatatransaction': {
            'Meta': {'ordering': "('-created', '-updated')", 'object_name': 'DocdataTransaction', '_ormbases': [u'payments.Transaction']},
            'authorization_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'authorization_currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'authorization_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'capture_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'capture_currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'capture_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'docdata_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'NEW'", 'max_length': '30'}),
            u'transaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payments.Transaction']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'payments_logger.paymentlogentry': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'PaymentLogEntry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['payments.Payment']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        u'projects.partnerorganization': {
            'Meta': {'object_name': 'PartnerOrganization'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        MODEL_MAP['project']['model_lower']: {
            'Meta': {'ordering': "['title']", 'object_name': MODEL_MAP['project']['class']},
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
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'organization'", 'null': 'True', 'to': "orm['{0}']".format(MODEL_MAP['organization']['model'])}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': "orm['{0}']".format(MODEL_MAP['user']['model'])}),
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
            'receiver': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receiver'", 'null': 'True', 'to': "orm['{0}']".format(MODEL_MAP['user']['model'])}),
            'receiver_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'receiver_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sender'", 'null': 'True', 'to': "orm['{0}']".format(MODEL_MAP['user']['model'])}),
            'sender_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'sender_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '20', 'db_index': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        }
    }

    complete_apps = ['payments', 'payments_docdata', 'payments_logger', 'cowry_docdata', 'fund']
    symmetrical = True
