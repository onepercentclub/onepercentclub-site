from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from bluebottle.bluebottle_drf2.views import RetrieveUpdateDeleteAPIView, ListCreateAPIView, ListAPIView
from rest_framework import permissions, exceptions

from bluebottle.utils.utils import get_project_model

PROJECT_MODEL = get_project_model()

from .models import FundRaiser
from .serializers import FundRaiserSerializer


class FundRaiserListView(ListCreateAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 4
    paginate_by_param = 'page_size'

    # because we overwrite get_queryset, this is ignored
    # TODO: Write cleaner code that takes this argument into account.
    # ordering = ('-created', )

    def get_queryset(self, queryset=None):
        queryset = super(FundRaiserListView, self).get_queryset(queryset)

        filter_kwargs = {}

        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = PROJECT_MODEL.objects.get(slug=project_slug)
            except PROJECT_MODEL.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': PROJECT_MODEL._meta.verbose_name})

            filter_kwargs['project'] = project

        user_id = self.request.QUERY_PARAMS.get('owner', None)
        if user_id:
            filter_kwargs['owner__pk'] = user_id

        return queryset.filter(**filter_kwargs).order_by('-created')

    def pre_save(self, obj):
        if not self.request.user.is_authenticated():
            raise exceptions.PermissionDenied()

        obj.owner = self.request.user


class FundRaiserDetailView(RetrieveUpdateDeleteAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
