from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from apps.bluebottle_utils.utils import get_client_ip
from apps.wallposts.serializers import WallpostReactionSerializer
from rest_framework import permissions
from django.contrib.contenttypes.models import ContentType
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView
from apps.reactions.models import Reaction
from apps.wallposts.models import WallPost


class WallPostReactionMixin(object):

    def get_queryset(self):
        queryset = super(WallPostReactionMixin, self).get_queryset()
        content_type = ContentType.objects.get_for_model(WallPost)
        queryset = queryset.filter(content_type=content_type)
        wallpost_id = self.request.QUERY_PARAMS.get('wallpost_id', None)
        print wallpost_id
        if wallpost_id:
            queryset = queryset.filter(object_id=wallpost_id)
        queryset = queryset.order_by("-created")
        return queryset

    def pre_save(self, obj):
        content_type = ContentType.objects.get_for_model(WallPost)
        obj.content_type_id = content_type.id
        obj.author = self.request.user
        obj.ip_address = get_client_ip(self.request)



class WallPostReactionList(WallPostReactionMixin, ListCreateAPIView):
    model = Reaction
    serializer_class = WallpostReactionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10


class WallPostReactionDetail(WallPostReactionMixin, RetrieveUpdateDeleteAPIView):
    model = Reaction
    serializer_class = WallpostReactionSerializer
    permission_classes = (IsAuthorOrReadOnly,)
