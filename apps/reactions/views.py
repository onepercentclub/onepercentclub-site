from rest_framework import generics
from rest_framework import permissions
from .models import Reaction
from .serializers import ReactionListSerializer, ReactionDetailSerializer


# API views

class ReactionRoot(generics.ListAPIView):
    model = Reaction
    serializer_class = ReactionListSerializer
    permissions_classes = (permissions.SAFE_METHODS,)
    paginate_by = 10


class ReactionInstance(generics.RetrieveAPIView):
    model = Reaction
    serializer_class = ReactionDetailSerializer
    permissions_classes = (permissions.SAFE_METHODS,)


# Django template Views

# None for now.