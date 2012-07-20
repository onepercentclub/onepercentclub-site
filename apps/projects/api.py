from tastypie.resources import ModelResource
from tastypie import fields, utils
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from .models import Project, IdeaPhase, PlanPhase, ActPhase, ResultsPhase


class ProjectResource(ModelResource):
#    ideaphase = fields.OneToOneField(
#                 'apps.projects.api.IdeaPhaseResource', 'ideaphase', full=True)
#    planphase = fields.OneToOneField(
#                 'projects.api.PlanPhaseResource', 'planphase', full=False)
#    actphase = fields.OneToOneField(
#                'projects.api.ActPhaseResource', 'actphase', full=False)
#    resultsphase = fields.OneToOneField(
#                'projects.api.ResultsPhaseResource', 'resultsphase', full=False)

    class Meta:
        queryset = Project.objects.select_related('IdeaPhase').filter(phase='plan').all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


class IdeaPhaseResource(ModelResource):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = IdeaPhase.objects.select_related('IdeaPhase').all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


class PlanPhaseResource(ModelResource):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = PlanPhase.objects.all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


class ActPhaseResource(ModelResource):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = ActPhase.objects.all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


class ResultsPhaseResource(ModelResource):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = ResultsPhase.objects.all()
        authentication = BasicAuthentication()
        authorization = DjangoAuthorization()


