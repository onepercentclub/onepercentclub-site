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
    Project, IdeaPhase, PlanPhase, ActPhase, ResultsPhase,
    Link, Testimonial, Message, BudgetCategory, BudgetLine
)

from .base import MigrateModel

from .mappings import (
    MappingMapping, EducateDateTimeMapping,
    NoneToStringMapping, OneToManyMapping, CountryMapping,
    SlugifyMapping, IdentityMapping, WebsiteMapping,
    StringToDecimalMapping, ConcatenatingStringMapping,
    PathToFileMapping
)

from .organizations import MigrateOrganization
from .accounts import MigrateMemberAuth


# We want a handy reference to these status objects
phases = Project.ProjectPhases
statuses = PlanPhase.PhaseStatuses


class PhaseMapping(IdentityMapping):
    """ Map a Project into its current phase. """

    def map_value(self, old_value):
        # Warning: realised is not part of the current phase mapping

        if old_value in ('wizard',):
            # Idea phase
            phase = phases.idea

        elif old_value in ('validated', 'confirmed'):
            # Plan phase
            phase = phases.plan

        elif old_value in ('done', 'closed'):
            # There is no way to discriminate by 'act' or 'results' phases
            # so, for now, default to results when donations have been
            # received
            phase = phases.results

        else:
            raise Exception(u"Could not map '%s' to a phase.", old_value)

        return phase


class MigrateProject(MigrateModel):
    from_model = LegacyProject
    to_model = Project

    def list_from(self):
        """
        For now, skip projects which we cannot migrate.
        """
        qs = super(MigrateProject, self).list_from()

        # Only migrate for available organizations
        m = MigrateOrganization()
        qs = qs.filter(organization__in=m.list_from())

        # We don't know how to map declined projects
        qs = qs.exclude(status='declined')

        # Exclude projects without a name or title, for now
        qs = qs.exclude(Q(name='') | Q(title=''))

        # Exclude test projects
        qs = qs.exclude(
            Q(name__contains='test') | Q(title__contains='test') | \
            Q(name__contains='proef') | Q(title__contains='proef')
        )

        # We don't know what to do with projects without a country set
        # qs = qs.exclude(country_id=0)

        return qs

    # Fields handled by project migration

    # Project fields we'll throw away
    throw_away_fields = {
        'action': None,
        'admin_comments': None,
        'sess_id': None,
        'catalog': None,
        'closed': None,
        'deleted': None,
        'derde_helft': None,
        'document': None,
        'earth_charter': None,
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

        # To be migrated later
        'link': None,
        'message': None,
        'task': None,
        'weblog': None,

        'projecttag': None,
        'tags': None,

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

    field_mapping = {
        'id': True,

        'name': SlugifyMapping('slug', verbose=False),
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
        'latitude': True,
        'longitude': True,

        'project_language': True,

        # Mapped to phase
        'description': None,
        'startdate': None,
        'enddate': None,
        'longdescription': None,
        'project_goals': None,
        'target_audience': None,
        'solve_poverty': None,
        'description_duurzaamheid': None,
        'expected_results': None,
        'how_support': None,
        'volunteers': None,
        'money_needed_club': None,
        'legacy_budget': None,
        'received_other_sources': None,
        'expected_other_sources': None,
    }

    field_mapping.update(throw_away_fields)


class MigrateIdea(MigrateProject):
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
            project__phase__in=(phases.idea, phases.plan, phases.results)
        )

        return qs

    mapped_in_project = {
        'name': None,
        'photo': None,
        'owner_usr': None,
        'owner_usr_id': None,
        'organization': None,
        'organization_id': None,

        'created': None,

        'country': None,
        'latitude': None,
        'longitude': None,

        'project_language': None
    }

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
            'validated': statuses.completed,
            'confirmed': statuses.completed,
            'realised': statuses.completed,

            'wizard': statuses.hidden,
        }, verbose=False),

    }

    field_mapping.update(MigrateProject.throw_away_fields)
    field_mapping.update(mapped_in_project)


class MigratePlan(MigrateProject):
    to_model = PlanPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigratePlan, self).list_from()

        qs = qs.filter(
            status__in=(
                'done', 'closed', 'validated', 'confirmed',
                'realised'
            )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigratePlan, self).list_to()

        qs = qs.filter(
            project__phase__in=(phases.plan, phases.results)
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

        'longdescription': 'what',
        'project_goals': 'goal',
        'target_audience': 'who',
        'solve_poverty': 'how',
        'description_duurzaamheid':
            NoneToStringMapping('sustainability', verbose=False),
        'expected_results': 'target',
        'how_support': NoneToStringMapping('needed_expertise'),
        'volunteers': 'needed_volunteers',

        'money_needed_club': OneToManyMapping(
            StringToDecimalMapping('money_asked', verbose=False),
            StringToDecimalMapping('money_total', verbose=False)
        ),

        'legacy_budget': 'budget_description',

        'received_other_sources': ConcatenatingStringMapping(
            to_field='money_other_sources',
            concatenate_with=('expected_other_sources',),
            concatenate_str='<br/>',
            verbose=False
        ),

        'expected_other_sources': None, #Already mapped above

    }

    field_mapping.update(MigrateProject.throw_away_fields)
    field_mapping.update(MigrateIdea.mapped_in_project)


class MigrateAct(MigrateProject):
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

    mapped_in_idea = {
        'longdescription': None,
        'project_goals': None,
        'target_audience': None,
        'solve_poverty': None,
        'description_duurzaamheid': None,
        'expected_results': None,
        'how_support': None,
        'volunteers': None,

        'money_needed_club': None,

        'legacy_budget': None,

        'received_other_sources': None,
        'expected_other_sources': None
    }


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

    field_mapping.update(MigrateProject.throw_away_fields)
    field_mapping.update(MigrateIdea.mapped_in_project)
    field_mapping.update(mapped_in_idea)


class MigrateResults(MigrateProject):
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

    field_mapping.update(MigrateProject.throw_away_fields)
    field_mapping.update(MigrateIdea.mapped_in_project)
    field_mapping.update(MigrateAct.mapped_in_idea)


class MigrateLink(MigrateModel):
    from_model = LegacyLink
    to_model = Link

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateLink, self).list_from()

        m = MigrateProject()
        project_list = m.list_from()

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
        member_list = m.list_from()

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
        # Skip for now (automagically overridden)
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


class MigrateBudgetCategory(MigrateModel):
    from_model = NeedCategory
    to_model = BudgetCategory

    field_mapping = {
        'id': True,

        'name': True,
        'description': NoneToStringMapping(verbose=False),
        'ordering': True,

        # It seems as though we are throwing away the hierarchical relation
        # here - which seems a rather bad idea.
        # 'parent': ...,

        'need': None,
        'needcategory': None,
        'name_en': None,
        'name_es': None,

    }


class MigrateBudgetLine(MigrateLink):
    from_model = Need
    to_model = BudgetLine

    def list_from(self):
        """ Selectively skip objects with nonesense data. """
        qs = super(MigrateBudgetLine, self).list_from()

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
        'category_id': True,

        'description': NoneToStringMapping(verbose=False),

        'money_needed': StringToDecimalMapping('money_amount', verbose=False),
    }
