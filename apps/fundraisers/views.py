from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from bluebottle.bluebottle_drf2.views import RetrieveUpdateDeleteAPIView, ListCreateAPIView, ListAPIView
from rest_framework import permissions, exceptions

from apps.projects.models import Project

from .models import FundRaiser
from .serializers import FundRaiserSerializer


class FundRaiserListView(ListCreateAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 4

    def get_queryset(self, queryset=None):
        queryset = super(FundRaiserListView, self).get_queryset(queryset)

        filter_kwargs = {}

        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': Project._meta.verbose_name})

            filter_kwargs['project'] = project

        user_id = self.request.QUERY_PARAMS.get('owner', None)
        if user_id:
            filter_kwargs['owner__pk'] = user_id

        # randomize results?
        return queryset.filter(**filter_kwargs).order_by('?')

    def pre_save(self, obj):
        if not self.request.user.is_authenticated():
            raise exceptions.PermissionDenied()

        obj.owner = self.request.user


class FundRaiserDetailView(RetrieveUpdateDeleteAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
