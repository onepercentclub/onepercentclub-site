from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from apps.bluebottle_utils.utils import get_client_ip
from apps.wallposts.serializers import WallPostReactionSerializer, WallPostSerializer
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView
from apps.reactions.models import Reaction
from apps.wallposts.models import WallPost


class WallPostList(ListCreateAPIView):
    model = WallPost
    permission_classes = (AllowNone,)
    serializer_class = WallPostSerializer
    paginate_by = 4


class WallPostReactionMixin(object):

    def get_queryset(self):
        queryset = super(WallPostReactionMixin, self).get_queryset()
        wallpost_id = self.request.QUERY_PARAMS.get('wallpost_id', None)
        if wallpost_id:
            queryset = queryset.filter(object_id=wallpost_id)
        else:
            content_type = ContentType.objects.get_for_model(WallPost)
            queryset = queryset.filter(content_type=content_type)
        queryset = queryset.order_by("created")
        return queryset

    def pre_save(self, obj):
        content_type = ContentType.objects.get_for_model(WallPost)
        obj.content_type_id = content_type.id
        if not hasattr(obj, 'author'):
            obj.author = self.request.user
        else:
            obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)


class WallPostReactionList(WallPostReactionMixin, ListCreateAPIView):
    model = Reaction
    serializer_class = WallPostReactionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10


class WallPostReactionDetail(WallPostReactionMixin, RetrieveUpdateDeleteAPIView):
    model = Reaction
    serializer_class = WallPostReactionSerializer
    permission_classes = (IsAuthorOrReadOnly,)
