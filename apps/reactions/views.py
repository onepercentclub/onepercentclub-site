from django.utils import timezone
from rest_framework import generics
from rest_framework import permissions
from .models import Reaction
from .permissions import IsOwnerOrReadOnly
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
                          IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user
        obj.editor = obj.owner
        obj.ip_address = get_client_ip(self.request)


class ReactionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Reaction
    serializer_class = ReactionDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.editor = self.request.user
        obj.ip_address = get_client_ip(self.request)
