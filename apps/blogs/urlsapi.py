from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import BlogPostList, BlogPostDetail, NewsPostPreviewList, NewsPostList, NewsPostDetail

urlpatterns = patterns('',
    # Blog Posts
    url(r'^posts/$', BlogPostList.as_view(), name='blog-post-list'),
    surl(r'^posts/<slug:s>$', BlogPostDetail.as_view(), name='blog-post-detail'),

    # News Items
    url(r'^preview/news/$', NewsPostPreviewList.as_view(), name='news-preview-list'),
    url(r'^news/$', NewsPostList.as_view(), name='news-post-list'),
    surl(r'^news/<slug:s>$', NewsPostDetail.as_view(), name='news-post-detail'),

)
