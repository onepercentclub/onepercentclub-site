from rest_framework import generics
from rest_framework import permissions
from .models import BlogPost
from .serializers import BlogPostPreviewSerializer, BlogPostDetailSerializer


# API views

class BlogPostList(generics.ListAPIView):
    model = BlogPost
    serializer_class = BlogPostPreviewSerializer
    permissions_classes = (permissions.SAFE_METHODS,)
    paginate_by = 10


class BlogPostDetail(generics.RetrieveAPIView):
    model = BlogPost
    serializer_class = BlogPostDetailSerializer
    permissions_classes = (permissions.SAFE_METHODS,)


# Django template Views

# None for now.