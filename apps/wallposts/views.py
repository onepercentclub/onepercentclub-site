from rest_framework import generics
from .serializers import WallPostSerializer
from .models import WallPost


class WallPostList(generics.ListAPIView):
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10


class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = WallPostSerializer


