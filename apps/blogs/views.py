from apps.blogs.serializers import BlogPostPreviewSerializer
from rest_framework import generics
from rest_framework import permissions
from .models import BlogPost
from .serializers import BlogPostSerializer


class BlogPostPreviewList(generics.ListAPIView):
    model = BlogPost
    serializer_class = BlogPostPreviewSerializer
    paginate_by = 10
    filter_fields = ('post_type', 'language')

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogPostPreviewList, self).get_queryset()
        qs = qs.published()
        return qs


class BlogPostList(generics.ListAPIView):
    model = BlogPost
    serializer_class = BlogPostSerializer
    paginate_by = 10
    filter_fields = ('post_type', 'language')

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogPostList, self).get_queryset()
        qs = qs.published()
        return qs


class BlogPostDetail(generics.RetrieveAPIView):
    model = BlogPost
    serializer_class = BlogPostSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogPostDetail, self).get_queryset()
        qs = qs.published()
        return qs
