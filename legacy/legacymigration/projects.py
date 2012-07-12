import logging
logger = logging.getLogger(__name__)

from legacy.legacyprojects.models import (
    Project as LegacyProject,
    Link as LegacyLink,
    Testimonial as LegacyTestimonial,
    Message as LegacyMessage
)

from apps.projects.models import (
    Project, IdeaPhase, PlanPhase, ActPhase, ResultsPhase,
    Link, Testimonial, Message
)

from .base import MigrateModel

from .mappings import (
    MappingMapping, EducateDateTimeMapping, SubstitutionMapping, Mapping,
    NoneToStringMapping, OneToManyMapping, CountryMapping,
    NoneToStringCroppingMapping, SlugifyMapping, IdentityMapping
)

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
            raise Exception("Could not map %s to a phase.", old_value)

        return phase


class MigrateProject(MigrateModel):
    from_model = LegacyProject
    to_model = Project

    field_mapping = {
        'id': True,

        'name': SlugifyMapping('slug'),
        'title': NoneToStringMapping(),

        # We'll do file objects later
        'phote': None,

        # Related objects will come later
        'owner': None,
        'organization': None,

        'status': PhaseMapping(),

        'created': EducateDateTimeMapping(),

        'country': CountryMapping(),
        'latitude': True,
        'longitude': True,

        'project_language': True
    }


class MigrateIdea(MigrateModel):
    from_model = LegacyProject
    to_model = IdeaPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateIdea, self).list_from(self)

        qs = qs.filter(
            status__in=(
                'done', 'closed', 'validated', 'confirmed',
                'realised', 'wizard'
            )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateIdea, self).list_to(self)

        qs = qs.filter(
            phase__in=(phases.idea, phases.plan, phases.results)
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
            'validated': statuses.completed,
            'confirmed': statuses.completed,
            'realised': statuses.completed,

            'wizard': statuses.hidden
        }),

        'longdescription': 'what',
        'project_goals': 'goal',
        'target_audience': 'who',
        'solve_poverty': 'how',
        'description_duurzaamheid': 'sustainability',
        'expected_results': 'target',
        'how_support': 'needed_expertise',
    }


class MigratePlan(MigrateModel):
    from_model = LegacyProject
    to_model = PlanPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigratePlan, self).list_from(self)

        qs = qs.filter(
            status__in=(
                'done', 'closed', 'validated', 'confirmed',
                'realised'
            )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigratePlan, self).list_to(self)

        qs = qs.filter(
            phase__in=(phases.plan, phases.results)
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
        })

    }


class MigrateAct(MigrateModel):
    from_model = LegacyProject
    to_model = ActPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateAct, self).list_from(self)

        qs = qs.filter(
            status__in=('done', 'closed', )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateAct, self).list_to(self)

        qs = qs.filter(
            phase__in=(phases.results, )
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
        })
    }


class MigrateResults(MigrateModel):
    from_model = LegacyProject
    to_model = ResultsPhase

    def list_from(self):
        """ Filter by project status. """
        qs = super(MigrateResults, self).list_from(self)

        qs = qs.filter(
            status__in=('done', 'closed', )
        )

        return qs

    def list_to(self):
        """ Filter by projects past idea phase. """
        qs = super(MigrateResults, self).list_to(self)

        qs = qs.filter(
            phase__in=(phases.results, )
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
        })
    }


class MigrateLink(MigrateModel):
    from_model = LegacyLink
    to_model = Link

    field_mapping = {
        'id': True,
    }


class MigrateTestimonial(MigrateModel):
    from_model = LegacyTestimonial
    to_model = Testimonial

    field_mapping = {
        'id': True,
    }


class MigrateMessage(MigrateModel):
    from_model = LegacyMessage
    to_model = Message

    field_mapping = {
        'id': True,
    }
