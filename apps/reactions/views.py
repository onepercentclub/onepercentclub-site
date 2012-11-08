from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import permissions
from .models import Reaction
from .permissions import IsAuthorOrReadOnly
from .serializers import ReactionListSerializer, ReactionDetailSerializer


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ReactionList(generics.ListCreateAPIView):
    model = Reaction
    serializer_class = ReactionListSerializer
    paginate_by = 10
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user
        obj.editor = obj.owner
        obj.ip_address = get_client_ip(self.request)
        reaction_to_instance = self._get_reaction_to_instance()
        obj.content_object = reaction_to_instance

    def get_queryset(self):
        reaction_to_instance = self._get_reaction_to_instance()
        return self.model.objects.for_content_type(self.kwargs['content_type']).filter(object_pk=reaction_to_instance.pk)

    def _get_reaction_to_instance(self):
        reaction_to_type = ContentType.objects.get_for_id(self.kwargs['content_type'])
        reaction_to_instance = reaction_to_type.get_object_for_this_type(slug=self.kwargs['slug'])
        return reaction_to_instance


class ReactionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Reaction
    serializer_class = ReactionDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

    def pre_save(self, obj):
        obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)
