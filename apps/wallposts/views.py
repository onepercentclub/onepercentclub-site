from bluebottle.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from bluebottle.bluebottle_utils.utils import set_author_editor_ip
from rest_framework import permissions
from bluebottle.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from .models import WallPost, Reaction
from .serializers import ReactionSerializer, WallPostSerializer


class WallPostList(ListAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    filter_fields = ('id',)
    paginate_by = 200

    def get_queryset(self):
        """
        Override get_queryset() to filter on multiple values for 'id'
        It seems that DRF2 doesn't have a implementation for filtering against an array of ids.
        https://groups.google.com/forum/?fromgroups#!topic/django-rest-framework/vbifEyharBw
        """
        queryset = super(WallPostList, self).get_queryset()
        id_list = self.request.GET.getlist('ids[]', None)
        if id_list:
            queryset = queryset.filter(id__in=id_list)
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
