from rest_framework import generics
from rest_framework import permissions
from .models import BlogPost
from .serializers import BlogPostPreviewSerializer, BlogPostDetailSerializer


# API views

class BlogPostRoot(generics.ListAPIView):
    model = BlogPost
    serializer_class = BlogPostPreviewSerializer
    permissions_classes = (permissions.SAFE_METHODS,)
    paginate_by = 10


class BlogPostInstance(generics.RetrieveAPIView):
    model = BlogPost
    serializer_class = BlogPostDetailSerializer
    permissions_classes = (permissions.SAFE_METHODS,)


# Django template Views

# None for now.