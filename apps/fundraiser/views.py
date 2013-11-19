from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from bluebottle.bluebottle_drf2.views import RetrieveUpdateDeleteAPIView, ListCreateAPIView

from apps.projects.models import Project

from .models import FundRaiser
from .serializers import FundRaiserSerializer


class FundRaiserListView(ListCreateAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    paginate_by = 4

    def get_queryset(self):
        queryset = super(FundRaiserListView, self).get_queryset()
        project_slug = self.request.QUERY_PARAMS.get('project', None)
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug)
            except Project.DoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                              {'verbose_name': queryset.model._meta.verbose_name})
        else:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

        queryset = queryset.filter(project=project)
        # randomize results?
        return queryset.order_by('?')


class FundRaiserDetailView(RetrieveUpdateDeleteAPIView):
    model = FundRaiser
    serializer_class = FundRaiserSerializer
    permission_classes = (IsAuthorOrReadOnly,)
