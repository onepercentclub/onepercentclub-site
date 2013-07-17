from apps.blogs.models import NewsPostProxy, BlogPostProxy
from apps.blogs.serializers import BlogPostPreviewSerializer
from rest_framework import generics
from rest_framework import permissions
from .models import BlogPost
from .serializers import BlogPostSerializer


class NewsPostPreviewList(generics.ListAPIView):
    model = NewsPostProxy
    serializer_class = BlogPostPreviewSerializer
    paginate_by = 5
    filter_fields = ('language', )

    def get_queryset(self, *args, **kwargs):
        qs = super(NewsPostPreviewList, self).get_queryset()
        qs = qs.published()
        return qs


class NewsPostList(generics.ListAPIView):
    model = NewsPostProxy
    serializer_class = BlogPostSerializer
    paginate_by = 5
    filter_fields = ('language', )

    def get_queryset(self, *args, **kwargs):
        qs = super(NewsPostList, self).get_queryset()
        qs = qs.published()
        return qs


class NewsPostDetail(generics.RetrieveAPIView):
    model = NewsPostProxy
    serializer_class = BlogPostSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super(NewsPostDetail, self).get_queryset()
        qs = qs.published()
        return qs


class BlogPostList(generics.ListAPIView):
    model = BlogPostProxy
    serializer_class = BlogPostSerializer
    paginate_by = 5
    filter_fields = ('language', )

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogPostList, self).get_queryset()
        qs = qs.published()
        return qs


class BlogPostDetail(generics.RetrieveAPIView):
    model = BlogPostProxy
    serializer_class = BlogPostSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super(BlogPostDetail, self).get_queryset()
        qs = qs.published()
        return qs
