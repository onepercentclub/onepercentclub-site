from rest_framework import generics
from rest_framework import permissions
from apps.likes.serializers import LikeSerializer
from .models import Like


class LikeList(generics.ListCreateAPIView):
    model = Like
    serializer_class = LikeSerializer