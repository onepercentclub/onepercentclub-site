import django_filters
from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from bluebottle.bluebottle_utils.utils import set_author_editor_ip
from rest_framework import permissions
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from apps.projects.models import Project
from .models import WallPost, Reaction
from .serializers import ReactionSerializer, WallPostSerializer


class WallPostFilter(django_filters.FilterSet):
    parent_type = django_filters.CharFilter(name="content_type__name")
    parent_id = django_filters.NumberFilter(name="object_id")

    class Meta:
        model = WallPost
        fields = ['parent_type', 'parent_id']


class WallPostList(ListCreateAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    filter_class = WallPostFilter
    paginate_by = 5

    def get_queryset(self):
        queryset = super(WallPostList, self).get_queryset()

        # Some custom filtering projects slugs.
        parent_type = self.request.QUERY_PARAMS.get('parent_type', None)
        parent_id = self.request.QUERY_PARAMS.get('parent_id', None)
        if parent_type == 'project' and parent_id:
            print "Yeah"
            try:
                project = Project.objects.get(slug=parent_id)
            except Project.DoesNotExist:
                return WallPost.objects.none()
            queryset = queryset.filter(object_id=project.id)

        queryset = queryset.order_by('-created')
        return queryset


class WallPostDetail(RetrieveUpdateDeleteAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    permission_classes = (IsAuthorOrReadOnly, )


class ReactionList(ListCreateAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    filter_fields = ('wallpost',)

    def pre_save(self, obj):
        set_author_editor_ip(self.request, obj)


class ReactionDetail(RetrieveUpdateDeleteAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def pre_save(self, obj):
        set_author_editor_ip(self.request, obj)
