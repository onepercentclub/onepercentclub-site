from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly, AllowNone
from apps.bluebottle_utils.utils import set_author_editor_ip
from rest_framework import permissions
from apps.bluebottle_drf2.views import ListCreateAPIView, RetrieveUpdateDeleteAPIView, ListAPIView
from .models import WallPost, Reaction
from .serializers import ReactionSerializer, WallPostSerializer



class WallPostList(ListAPIView):
    model = WallPost
    permission_classes = (AllowNone,)
    serializer_class = WallPostSerializer
    paginate_by = 4


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
