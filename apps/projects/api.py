from tastypie.resources import ModelResource
from tastypie import fields, utils
from tastypie.authorization import DjangoAuthorization

from .models import Project, IdeaPhase, PlanPhase, ActPhase, ResultsPhase

class ResourceBase(ModelResource):
    class Meta:
        authorization = DjangoAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']



class ProjectResource(ResourceBase):
#    ideaphase = fields.OneToOneField(
#                 'apps.projects.api.IdeaPhaseResource', 'ideaphase', full=True)
#    planphase = fields.OneToOneField(
#                 'projects.api.PlanPhaseResource', 'planphase', full=False)
#    actphase = fields.OneToOneField(
#                'projects.api.ActPhaseResource', 'actphase', full=False)
#    resultsphase = fields.OneToOneField(
#                'projects.api.ResultsPhaseResource', 'resultsphase', full=False)

    class Meta:
        queryset = Project.objects.filter(phase='plan').all()
        filtering = {
             "latitude": ('gte', 'lte'),
             "longitude": ('gte', 'lte'),
             "title": ('startswith', 'contains')
        }

class IdeaPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = IdeaPhase.objects.select_related('IdeaPhase').all()


class PlanPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = PlanPhase.objects.all()


class ActPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = ActPhase.objects.all()


class ResultsPhaseResource(ResourceBase):
    project = fields.OneToOneField(ProjectResource, 'project')

    class Meta:
        queryset = ResultsPhase.objects.all()


