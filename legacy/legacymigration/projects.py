import logging
logger = logging.getLogger(__name__)

import settings

from django.db.models import Q

from legacy.legacyprojects.models import (
    Project as LegacyProject,
    Link as LegacyLink,
    Testimonial as LegacyTestimonial,
    Message as LegacyMessage,
    NeedCategory, Need
)

from apps.projects.models import (
    Project, IdeaPhase, FundPhase, ActPhase, ResultsPhase,
    Link, Testimonial, Message, BudgetLine, PartnerOrganization
)

from .base import MigrateModel, UniqueSlugMixin

from .mappings import (
    MappingMapping, EducateDateTimeMapping,
    NoneToStringMapping, OneToManyMapping, CountryMapping,
    TolerantSlugifyCroppingMapping, IdentityMapping, WebsiteMapping,
    StringToDecimalMapping, ConcatenatingStringMapping,
    PathToFileMapping
)

from .organizations import MigrateOrganization
from .accounts import MigrateMemberAuth
from .tags import copy_tags, test_tags


# We want a handy reference to these status objects
phases = Project.ProjectPhases
statuses = FundPhase.PhaseStatuses


class PhaseMapping(IdentityMapping):
    """ Map a Project into its current phase. """

    def map_value(self, old_value):
        # Warning: realised is not part of the current phase mapping

        if old_value in ('wizard', 'created', 'declined'):
            # Idea phase
            phase = phases.idea

        elif old_value in ('validated', 'confirmed'):
            # Fund phase
            phase = phases.fund

        elif old_value in ('done', 'closed'):
            # There is no way to discriminate by 'act' or 'results' phases
            # so, for now, default to results when donations have been
            # received
            phase = phases.results

        else:
            raise Exception(u"Could not map '%s' to a phase.", old_value)

        return phase


class PartnerMapping(IdentityMapping):
    """ migrate projects with partner organizations """
    
    def get_partner_organization(self, slug):
        try:
            org = PartnerOrganization.objects.get(slug=slug)
            return org
        except PartnerOrganization.DoesNotExist:
            logger.error(u"PartnerOrganization %s not foud. " +
              "Did you load fixture project_partnerorganization_data.json.", slug)
        return False
    
    def map(self, instance, from_field):
        old_value = getattr(instance, from_field)
        new_value = None
        
        if getattr(instance, 'derde_helft'):
            new_value = self.get_partner_organization('derde_helft')
        if getattr(instance, 'earth_charter'):
            new_value = self.get_partner_organization('earth_charter')
        if getattr(instance, 'macro_micro'):
            new_value = self.get_partner_organization('macro_micro')
        return {self.get_to_field(from_field): new_value}
    
       
    def check(self, from_instance, to_instance, from_field):
        org = getattr(to_instance, 'partner_organization')
        if org == None:
            # If there's no partner org then these
            # values shouldnt be set
            if getattr(from_instance, 'derde_helft'):
                return False
            if getattr(from_instance, 'earth_charter'):
                return False
            if getattr(from_instance, 'macro_micro'):
                return False
            return True      
        elif getattr(from_instance, 'derde_helft'):
            if org.slug == 'derde_helft':
                return True
            return False
        elif getattr(from_instance, 'earth_charter'):
            if org.slug == 'earth_charter':
                return True
            return False
        elif getattr(from_instance, 'macro_micro'):
            if org.slug == 'macro_micro':
                return True
            return False
        return False



class MigrateProjectBase(MigrateModel):
    from_model = LegacyProject
    to_model = Project

    def list_from_exclusions(self, qs):
        """ Perform explicit exclusions on the queryset for dirty data. """

        # Exclude projects without a name or title, for now
        qs = qs.exclude(Q(name='') | Q(title=''))

        # Exclude test projects
        qs = qs.exclude(
            Q(name__contains='test') | Q(title__contains='test') | \
            Q(name__contains='proef') | Q(title__contains='proef')
        )

        return qs

    def list_from(self):
        """
        For now, skip projects which we cannot migrate.
        """
        qs = super(MigrateProjectBase, self).list_from()

        # Only migrate for available organizations
        m = MigrateOrganization()
        qs = qs.filter(organization__in=m._list_from())

        return qs


    # Fields handled by project & phaser
    mapped_in_project = {
        'name': None,
        'status': None,
        'photo': None,
        'owner_usr': None,
        'owner_usr_id': None,
        'organization': None,
        'organization_id': None,
        'derde_helft': None,
        'macro_micro': None,
        'earth_charter': None,
        'created': None,
        'country': None,
        'latitude': None,
        'longitude': None,
        'project_language': None
    }
    
    mapped_in_idea = {
        'how_support': None,
        'volunteers': None,
        'money_needed_for': None
    }

    mapped_in_fund = {
        'expected_results': None,
        'longdescription':None,
        'money_needed_club': None,
        'target_audience': None,
        'solve_poverty': None,              
        'description_duurzaamheid':None,
        'received_other_sources':None,
        'expected_other_sources': None    
    }

    mapped_in_act = {
        'planning': None,
        'startdate': None,
        'enddate': None,
    }
    
    
    mapped_in_results = {
    }
    
    

    # Project fields we'll throw away
    throw_away_fields = {
        'action': None,
        'admin_comments': None,
        'sess_id': None,
        'closed': None,
        'deleted': None,
        'document': None,
        'folder': None,
        'goal': None,
        'picture': None,
        'planning': None,
        'portfolioline': None,
        'project_goals': None,
        'realised': None,
        'video': None,
        'reported': None,
        'testimonial': None,
        'validated': None,
        'legacy_budget': None,

        # Explicitly mapped by MigrateProjectAlbums
        'catalog': None,

        # To be migrated later
        'link': None,
        'message': None,
        'task': None,
        'weblog': None,
        'tags' : None,

        'projecttag': None,

        'rate_count': None,
        'rate_current': None,
        'rating': None,

        # Donations and money
        'donationline': None,
        'settlement': None,
        'projectdonations': None,

        'money_needed_for': None,
        'need': None,


    }


class MigrateProject(UniqueSlugMixin, MigrateProjectBase):
    """ Migrations for projects. """

    def migrate_single(self, from_instance, to_instance):
        """
        Override migrate_single so that tags can be copied over using the
        Taggit manager.
        """
        super(MigrateProject, self).migrate_single(from_instance, to_instance)

        copy_tags(from_instance, to_instance)

    def test_single(self, from_instance, to_instance):
        """
        Override test_single so that the tags that have been copied over using
        the Taggit manager can be tested.
        """
        super_result = super(MigrateProject, self).test_single(from_instance, to_instance)

        tags_result = test_tags(from_instance, to_instance, logger)

        return super_result and tags_result


    field_mapping = {
        'id': True,

        'name': TolerantSlugifyCroppingMapping(
            100, to_field='slug', verbose=False
        ),
        'title': NoneToStringMapping(),

        'photo': PathToFileMapping(
            root_path=settings.LEGACY_MEDIA_ROOT,
            allow_missing=True,
            to_field='image',
            verbose=False
        ),

        # Map related PK's for owner and organization directly
        'owner_usr': None,
        'owner_usr_id': 'owner_id',
        'organization': None,
        'organization_id': True,

        'status': PhaseMapping('phase', verbose=False),

        'created': EducateDateTimeMapping(verbose=False),

        'country': CountryMapping(verbose=False),
        'latitude': StringToDecimalMapping(verbose=False),
        'longitude': StringToDecimalMapping(verbose=False),

        'derde_helft': PartnerMapping('partner_organization', verbose=False),
        'earth_charter': None, # one by derde_helft 
        'macro_micro': None, # Done by derde_helft

        'project_language': True,

        # Tags are copied over in migrate_single().
        'tags': None,
        
        # Migrated in phases
        'description': None

    }

    field_mapping.update(MigrateProjectBase.throw_away_fields)
    field_mapping.update(MigrateProjectBase.mapped_in_idea)
    field_mapping.update(MigrateProjectBase.mapped_in_fund)
    field_mapping.update(MigrateProjectBase.mapped_in_act)
    field_mapping.update(MigrateProjectBase.mapped_in_results)


class MigrateIdea(MigrateProjectBase):
    to_model = IdeaPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateIdea, self).list_from()

        qs = qs.filter(
            status__in=(
                'done', 'closed', 'validated', 'confirmed',
                'realised', 'wizard'
            )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateIdea, self).list_to()

        qs = qs.filter(
            project__phase__in=(phases.idea, phases.fund, phases.results)
        )

        return qs

    field_mapping = {
        'id': OneToManyMapping(
            IdentityMapping('id'),
            IdentityMapping('project_id')
        ),
        'title': NoneToStringMapping(),
        'description': NoneToStringMapping(),
        'startdate': True,
        'enddate': True,
        
        'volunteers': ConcatenatingStringMapping(
            to_field='knowledge_description',
            concatenate_with=('how_support',),
            concatenate_str='<br />',
            verbose=False
        ),
                     
        'money_needed_for': NoneToStringMapping('money_description'),

        'status': MappingMapping({
            'done': statuses.completed,
            'closed': statuses.completed,
            'validated': statuses.completed,
            'confirmed': statuses.completed,
            'realised': statuses.completed,

            'wizard': statuses.hidden,
        }, verbose=False),
                     
    }

    field_mapping.update(MigrateProjectBase.throw_away_fields)
    field_mapping.update(MigrateProjectBase.mapped_in_project)
    field_mapping.update(MigrateProjectBase.mapped_in_fund)
    field_mapping.update(MigrateProjectBase.mapped_in_act)
    field_mapping.update(MigrateProjectBase.mapped_in_results)


class MigrateFund(MigrateProjectBase):
    to_model = FundPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateFund, self).list_from()

        qs = qs.filter(
            status__in=(
                'done', 'closed', 'validated', 'confirmed',
                'realised'
            )
        )
        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateFund, self).list_to()
        qs = qs.filter(
            project__phase__in=(phases.fund, phases.results)
        )
        return qs


    field_mapping = {
        'id': OneToManyMapping(
            IdentityMapping('id'),
            IdentityMapping('project_id')
        ),
        'title': NoneToStringMapping(),
        'description': NoneToStringMapping(),
        'startdate': True,
        'enddate': True,

        'status': MappingMapping({
            'done': statuses.completed,
            'closed': statuses.completed,
            'realised': statuses.completed,

            'confirmed': statuses.progress,
            'validated': statuses.progress
        }, verbose=False),

        'longdescription': ConcatenatingStringMapping(
            to_field='description_long',
            concatenate_with=('project_goals', 'expected_results',),
            concatenate_str='<br/>',
            verbose=False
        ),
        'target_audience': ConcatenatingStringMapping(
            to_field='social_impact',
            concatenate_with=('solve_poverty',),
            concatenate_str='<br/>',
            verbose=False,
        ),
        'solve_poverty': None, # Already mapped above             
        'description_duurzaamheid':
            NoneToStringMapping('sustainability', verbose=False),
        'expected_results': None, # Already mapped above
        'money_needed_club': OneToManyMapping(
            StringToDecimalMapping('money_asked', verbose=False),
            StringToDecimalMapping('budget_total', verbose=False)
        ),
        'received_other_sources': ConcatenatingStringMapping(
            to_field='money_other_sources',
            concatenate_with=('expected_other_sources',),
            concatenate_str='<br/>',
            verbose=False
        ),

        'expected_other_sources': None, #Already mapped above

    }

    field_mapping.update(MigrateProjectBase.throw_away_fields)
    field_mapping.update(MigrateProjectBase.mapped_in_project)
    field_mapping.update(MigrateProjectBase.mapped_in_idea)
    field_mapping.update(MigrateProjectBase.mapped_in_act)
    field_mapping.update(MigrateProjectBase.mapped_in_results)


class MigrateAct(MigrateProjectBase):
    to_model = ActPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateAct, self).list_from()

        qs = qs.filter(
            status__in=('done', 'closed', )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateAct, self).list_to()

        qs = qs.filter(
            project__phase__in=(phases.results, )
        )

        return qs


    field_mapping = {
        'id': OneToManyMapping(
            IdentityMapping('id'),
            IdentityMapping('project_id')
        ),
        'title': NoneToStringMapping(),
        'description': NoneToStringMapping(),
        'startdate': True,
        'enddate': True,

        'status': MappingMapping({
            'done': statuses.completed,
            'closed': statuses.completed,
        }, verbose=False),

        'planning': True
    }

    field_mapping.update(MigrateProjectBase.throw_away_fields)
    field_mapping.update(MigrateProjectBase.mapped_in_project)
    field_mapping.update(MigrateProjectBase.mapped_in_idea)
    field_mapping.update(MigrateProjectBase.mapped_in_fund)
    field_mapping.update(MigrateProjectBase.mapped_in_results)


class MigrateResults(MigrateProjectBase):
    to_model = ResultsPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateResults, self).list_from()

        qs = qs.filter(
            status__in=('done', 'closed', )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateResults, self).list_to()

        qs = qs.filter(
            project__phase__in=(phases.results, )
        )

        return qs


    field_mapping = {
        'id': OneToManyMapping(
            IdentityMapping('id'),
            IdentityMapping('project_id')
        ),
        'title': NoneToStringMapping(),
        'description': NoneToStringMapping(),
        'startdate': True,
        'enddate': True,

        'status': MappingMapping({
            'done': statuses.completed,
            'closed': statuses.completed,
        }, verbose=False),
    }

    field_mapping.update(MigrateProjectBase.throw_away_fields)
    field_mapping.update(MigrateProjectBase.mapped_in_project)
    field_mapping.update(MigrateProjectBase.mapped_in_idea)
    field_mapping.update(MigrateProjectBase.mapped_in_fund)
    field_mapping.update(MigrateProjectBase.mapped_in_act)


class MigrateLink(MigrateModel):
    from_model = LegacyLink
    to_model = Link

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateLink, self).list_from()

        m = MigrateProject()
        project_list = m._list_from()

        qs = qs.filter(project__in=project_list)

        return qs

    field_mapping = {
        'id': True,

        'project': None,
        'project_id': True,

        'name': True,
        'url': WebsiteMapping(),
        'description': True,
        'ordering': True

    }


class MigrateTestimonial(MigrateLink):
    from_model = LegacyTestimonial
    to_model = Testimonial

    def list_from(self):
        """ Only filter addresses for migrated members. """
        qs = super(MigrateTestimonial, self).list_from()

        m = MigrateMemberAuth()
        member_list = m._list_from()

        qs = qs.filter(member__in=member_list)

        return qs

    field_mapping = {
        'id': True,

        'project': None,
        'project_id': True,

        'member': None,
        'member_id': 'user_id',

        'description': True,

        'created': EducateDateTimeMapping(verbose=False),
        # Skip for now (automagically overridden in database)
        #'updated': EducateDateTimeMapping()
    }


class MigrateMessage(MigrateTestimonial):
    from_model = LegacyMessage
    to_model = Message

    field_mapping = {
        'id': True,

        'project': None,
        'project_id': True,

        'member': None,
        'member_id': 'user_id',

        'text': 'body',

        'created': EducateDateTimeMapping(verbose=False),
        'deleted': EducateDateTimeMapping(verbose=False)
    }


class MigrateBudgetLine(MigrateLink):
    from_model = Need
    to_model = BudgetLine

    def list_from_exclusions(self, qs):
        """ Perform explicit exclusions on the queryset for dirty data. """

        # There is exactly one item with a money_needed of
        # 564564654.<something>, with a bogus description.
        # It has too many decimals, so ignore it for now.
        qs = qs.exclude(pk=1469)

        return qs

    field_mapping = {
        'id': True,

        'project': None,
        'project_id': True,

        'category': None,
        'category_id': None,

        'description': NoneToStringMapping(verbose=False),

        'money_needed': StringToDecimalMapping('money_amount', verbose=False),
    }
