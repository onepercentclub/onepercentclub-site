from rest_framework import generics
from .serializers import MediaWallPostSerializer
from .models import WallPost


class WallPostList(generics.ListAPIView):
    model = WallPost
    serializer_class = MediaWallPostSerializer
    paginate_by = 10


class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = MediaWallPostSerializer


