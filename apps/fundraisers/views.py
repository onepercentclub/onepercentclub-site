from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from bluebottle.bluebottle_drf2.views import RetrieveUpdateDeleteAPIView, ListCreateAPIView
from rest_framework import permissions, exceptions

from apps.projects.models import Project

from .models import FundRaiser
from .serializers import FundRaiserSerializer


class FundRaiserListView(ListCreateAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 4

    def get_queryset(self):
        queryset = super(FundRaiserListView, self).get_queryset()
        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': Project._meta.verbose_name})
        else:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        queryset = queryset.filter(project=project)
        # randomize results?
        return queryset.order_by('?')

    def pre_save(self, obj):
        if not self.request.user.is_authenticated():
            raise exceptions.PermissionDenied()

        obj.owner = self.request.user


class FundRaiserDetailView(RetrieveUpdateDeleteAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
