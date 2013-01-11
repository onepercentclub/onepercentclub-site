from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import permissions
from apps.bluebottle_utils.utils import get_client_ip
from .models import Reaction
from apps.bluebottle_drf2.permissions import IsAuthorOrReadOnly
from .serializers import ReactionSerializer


class ReactionList(generics.ListCreateAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    paginate_by = 100
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # get a param from either kwargs, QUERY_PARAMS or DATA
    def get_param(self, param):
        if self.kwargs.get(param, None):
            return self.kwargs.get(param)
        if self.request.QUERY_PARAMS.get(param, None):
            return self.request.QUERY_PARAMS.get(param)
        if self.request.DATA.get(param, None):
            return self.request.DATA.get(param)
        return None

    def get_content_type(self):
        object_type = self.get_param('object_type')


    def pre_save(self, obj):
        obj.author = self.request.user
        obj.editor = obj.author
        obj.ip_address = get_client_ip(self.request)
        reaction_to_instance = self._get_reactions_to_instance()
        obj.content_object = reaction_to_instance

    def get_queryset(self):
        queryset = super(ReactionList, self).get_queryset()
        if self.get_content_type():
            queryset = queryset.filter(content_type=self.get_content_type())
        if self.get_object_id():
            queryset = queryset.filter(object_id=self.get_object_id())
        queryset = queryset.order_by("-created")
        return queryset


class ReactionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Reaction
    serializer_class = ReactionSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def pre_save(self, obj):
        obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)
