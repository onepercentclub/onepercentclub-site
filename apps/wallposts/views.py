import django_filters
from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from bluebottle.bluebottle_utils.utils import set_author_editor_ip
from rest_framework import permissions
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from .models import WallPost, Reaction
from .serializers import ReactionSerializer, WallPostSerializer


class WallPostFilter(django_filters.FilterSet):
    module = django_filters.CharFilter(name="content_type__name")
    parent_id = django_filters.NumberFilter(name="object_id")

    class Meta:
        model = WallPost
        fields = ['module', 'parent_id']


class WallPostList(ListCreateAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    filter_class = WallPostFilter
    paginate_by = 5

    def get_queryset(self):
        if 'project' == self.request.QUERY_PARAMS

        queryset = super(WallPostList, self).get_queryset()
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
