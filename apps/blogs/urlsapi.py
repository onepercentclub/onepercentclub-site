from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import BlogPostList, BlogPostDetail

urlpatterns = patterns('',
    url(r'^$', BlogPostList.as_view(), name='blogpost-root'),
    surl(r'^<slug:s>$', BlogPostDetail.as_view(), name='blogpost-instance'),
)
