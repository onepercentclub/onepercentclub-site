from django.conf.urls import patterns, url, include
from django.contrib.contenttypes.models import ContentType
from surlex.dj import surl
from .views import BlogPostList, BlogPostDetail
from .models import BlogPost

urlpatterns = patterns('',
    url(r'^$', BlogPostList.as_view(), name='blogpost-root'),
    surl(r'^<slug:s>/reactions/', include('apps.reactions.urlsapi', namespace='reactions'), {'content_type': ContentType.objects.get_for_model(BlogPost).id}),
    surl(r'^<slug:s>$', BlogPostDetail.as_view(), name='blogpost-instance'),
)
