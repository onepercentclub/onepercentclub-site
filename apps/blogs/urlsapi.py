from apps.blogs.views import BlogPostPreviewList
from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import BlogPostList, BlogPostDetail

urlpatterns = patterns('',
    url(r'^previews/$', BlogPostPreviewList.as_view(), name='blog-preview-list'),
    url(r'^posts/$', BlogPostList.as_view(), name='blog-post-list'),
    surl(r'^posts/<slug:s>$', BlogPostDetail.as_view(), name='blog-post-detail'),
)
