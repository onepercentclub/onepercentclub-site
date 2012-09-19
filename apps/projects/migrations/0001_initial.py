# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ('media', '0001_initial'),
        ('geo', '0001_initial'),
        ('organizations', '0001_initial')
    )

    def forwards(self, orm):
        # Adding model 'ProjectTheme'
        db.create_table('projects_projecttheme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('projects', ['ProjectTheme'])

        # Adding model 'Project'
        db.create_table('projects_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
            ('partner_organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.PartnerOrganization'], null=True, blank=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=255, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['organizations.Organization'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('phase', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=21, decimal_places=18)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=21, decimal_places=18)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['geo.Country'], null=True, blank=True)),
            ('project_language', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('projects', ['Project'])

        # Adding M2M table for field themes on 'Project'
        db.create_table('projects_project_themes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['projects.project'], null=False)),
            ('projecttheme', models.ForeignKey(orm['projects.projecttheme'], null=False))
        ))
        db.create_unique('projects_project_themes', ['project_id', 'projecttheme_id'])

        # Adding M2M table for field albums on 'Project'
        db.create_table('projects_project_albums', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['projects.project'], null=False)),
            ('album', models.ForeignKey(orm['media.album'], null=False))
        ))
        db.create_unique('projects_project_albums', ['project_id', 'album_id'])

        # Adding model 'PartnerOrganization'
        db.create_table('projects_partnerorganization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('projects', ['PartnerOrganization'])

        # Adding model 'IdeaPhase'
        db.create_table('projects_ideaphase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['projects.Project'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('startdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('knowledge_description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('projects', ['IdeaPhase'])

        # Adding model 'FundPhase'
        db.create_table('projects_fundphase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['projects.Project'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('startdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description_long', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('budget_total', self.gf('apps.bluebottle_utils.fields.MoneyField')(max_digits=9, decimal_places=2)),
            ('money_asked', self.gf('apps.bluebottle_utils.fields.MoneyField')(max_digits=9, decimal_places=2)),
            ('sustainability', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('money_other_sources', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('social_impact', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('impact_group', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('impact_direct_male', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('impact_direct_female', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('impact_indirect_male', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
            ('impact_indirect_female', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=6)),
        ))
        db.send_create_signal('projects', ['FundPhase'])

        # Adding model 'ActPhase'
        db.create_table('projects_actphase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['projects.Project'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('startdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('planning', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('planned_start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('planned_end_date', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('projects', ['ActPhase'])

        # Adding model 'ResultsPhase'
        db.create_table('projects_resultsphase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['projects.Project'], unique=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('startdate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('enddate', self.gf('django.db.models.fields.DateField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('what', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tips', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('change', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('financial', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('next', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('projects', ['ResultsPhase'])

        # Adding model 'Referals'
        db.create_table('projects_referals', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('projects', ['Referals'])

        # Adding model 'BudgetLine'
        db.create_table('projects_budgetline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('money_amount', self.gf('apps.bluebottle_utils.fields.MoneyField')(max_digits=9, decimal_places=2)),
        ))
        db.send_create_signal('projects', ['BudgetLine'])

        # Adding model 'Link'
        db.create_table('projects_link', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal('projects', ['Link'])

        # Adding model 'Testimonial'
        db.create_table('projects_testimonial', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal('projects', ['Testimonial'])

        # Adding model 'Message'
        db.create_table('projects_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('deleted', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('projects', ['Message'])


    def backwards(self, orm):
        # Deleting model 'ProjectTheme'
        db.delete_table('projects_projecttheme')

        # Deleting model 'Project'
        db.delete_table('projects_project')

        # Removing M2M table for field themes on 'Project'
        db.delete_table('projects_project_themes')

        # Removing M2M table for field albums on 'Project'
        db.delete_table('projects_project_albums')

        # Deleting model 'PartnerOrganization'
        db.delete_table('projects_partnerorganization')

        # Deleting model 'IdeaPhase'
        db.delete_table('projects_ideaphase')

        # Deleting model 'FundPhase'
        db.delete_table('projects_fundphase')

        # Deleting model 'ActPhase'
        db.delete_table('projects_actphase')

        # Deleting model 'ResultsPhase'
        db.delete_table('projects_resultsphase')

        # Deleting model 'Referals'
        db.delete_table('projects_referals')

        # Deleting model 'BudgetLine'
        db.delete_table('projects_budgetline')

        # Deleting model 'Link'
        db.delete_table('projects_link')

        # Deleting model 'Testimonial'
        db.delete_table('projects_testimonial')

        # Deleting model 'Message'
        db.delete_table('projects_message')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'geo.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alpha2_code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'alpha3_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'oda_recipient': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subregion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.SubRegion']"})
        },
        'geo.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        'geo.subregion': {
            'Meta': {'ordering': "['name']", 'object_name': 'SubRegion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numeric_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Region']"})
        },
        'media.album': {
            'Meta': {'object_name': 'Album'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        },
        'organizations.organization': {
            'Meta': {'ordering': "['name']", 'object_name': 'Organization'},
            'account_bank_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_bank_country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Country']", 'null': 'True', 'blank': 'True'}),
            'account_bank_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_bicswift': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_iban': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'account_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legal_status': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'partner_organisations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'projects.actphase': {
            'Meta': {'object_name': 'ActPhase'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'planned_end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'planned_start_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'planning': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['projects.Project']", 'unique': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'projects.budgetline': {
            'Meta': {'object_name': 'BudgetLine'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'money_amount': ('apps.bluebottle_utils.fields.MoneyField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"})
        },
        'projects.fundphase': {
            'Meta': {'object_name': 'FundPhase'},
            'budget_total': ('apps.bluebottle_utils.fields.MoneyField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_long': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impact_direct_female': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'impact_direct_male': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'impact_group': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'impact_indirect_female': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'impact_indirect_male': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '6'}),
            'money_asked': ('apps.bluebottle_utils.fields.MoneyField', [], {'max_digits': '9', 'decimal_places': '2'}),
            'money_other_sources': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['projects.Project']", 'unique': 'True'}),
            'social_impact': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sustainability': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'projects.ideaphase': {
            'Meta': {'object_name': 'IdeaPhase'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'knowledge_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['projects.Project']", 'unique': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'projects.link': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'projects.message': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'projects.partnerorganization': {
            'Meta': {'object_name': 'PartnerOrganization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'projects.project': {
            'Meta': {'ordering': "['title']", 'object_name': 'Project'},
            'albums': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['media.Album']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['geo.Country']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '255', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '21', 'decimal_places': '18'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '21', 'decimal_places': '18'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['organizations.Organization']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'partner_organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.PartnerOrganization']", 'null': 'True', 'blank': 'True'}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project_language': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['projects.ProjectTheme']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'projects.projecttheme': {
            'Meta': {'ordering': "['name']", 'object_name': 'ProjectTheme'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'projects.referals': {
            'Meta': {'object_name': 'Referals'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'projects.resultsphase': {
            'Meta': {'object_name': 'ResultsPhase'},
            'change': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'financial': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'next': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['projects.Project']", 'unique': 'True'}),
            'startdate': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'tips': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'what': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'projects.testimonial': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Testimonial'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['projects']