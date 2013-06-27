# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Slide.tab_text'
        db.add_column(u'banners_slide', 'tab_text',
                      self.gf('django.db.models.fields.CharField')(default='klik', max_length=100),
                      keep_default=False)

        # Adding field 'Slide.body'
        db.add_column(u'banners_slide', 'body',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Slide.image'
        db.add_column(u'banners_slide', 'image',
                      self.gf('sorl.thumbnail.fields.ImageField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Slide.background_image'
        db.add_column(u'banners_slide', 'background_image',
                      self.gf('sorl.thumbnail.fields.ImageField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Slide.link_text'
        db.add_column(u'banners_slide', 'link_text',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=400, blank=True),
                      keep_default=False)

        # Adding field 'Slide.link_url'
        db.add_column(u'banners_slide', 'link_url',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=400, blank=True),
                      keep_default=False)

        # Adding field 'Slide.style'
        db.add_column(u'banners_slide', 'style',
                      self.gf('django.db.models.fields.CharField')(default='default', max_length=40, blank=True),
                      keep_default=False)


        # Changing field 'Slide.title'
        db.alter_column(u'banners_slide', 'title', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):
        # Deleting field 'Slide.tab_text'
        db.delete_column(u'banners_slide', 'tab_text')

        # Deleting field 'Slide.body'
        db.delete_column(u'banners_slide', 'body')

        # Deleting field 'Slide.image'
        db.delete_column(u'banners_slide', 'image')

        # Deleting field 'Slide.background_image'
        db.delete_column(u'banners_slide', 'background_image')

        # Deleting field 'Slide.link_text'
        db.delete_column(u'banners_slide', 'link_text')

        # Deleting field 'Slide.link_url'
        db.delete_column(u'banners_slide', 'link_url')

        # Deleting field 'Slide.style'
        db.delete_column(u'banners_slide', 'style')


        # Changing field 'Slide.title'
        db.alter_column(u'banners_slide', 'title', self.gf('django.db.models.fields.CharField')(max_length=200))

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
        u'banners.slide': {
            'Meta': {'ordering': "('language', 'sequence')", 'object_name': 'Slide'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.BlueBottleUser']"}),
            'background_image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'link_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'link_url': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '20', 'db_index': 'True'}),
            'style': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '40', 'blank': 'True'}),
            'tab_text': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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

    complete_apps = ['banners']