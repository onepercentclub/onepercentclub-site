from django.conf.urls import patterns, url, include
from django.contrib.contenttypes.models import ContentType
from surlex.dj import surl
from .models import Project
from .views import (ProjectDetail, ProjectList, ProjectWallPostList, ProjectWallPostDetail,
                    ProjectMediaWallPostList, ProjectMediaWallPostDetail, ProjectTextWallPostList)


urlpatterns = patterns('',
    url(r'^$', ProjectList.as_view(), name='project-list'),
    surl(r'^<slug:s>/wallposts/', include('apps.wallposts.urlsapi', namespace='wallposts'), {'content_type': ContentType.objects.get_for_model(Project).id}),
    url(r'^(?P<pk>[0-9]+)$', ProjectDetail.as_view(), name='project-detail'),
    url(r'^wallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    url(r'^wallposts/(?P<pk>[0-9]+)$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
    url(r'^mediawallposts/$', ProjectMediaWallPostList.as_view(), name='project-mediawallpost-list'),
    url(r'^mediawallposts/(?P<pk>[0-9]+)$', ProjectMediaWallPostDetail.as_view(), name='project-mediawallpost-detail'),
    url(r'^textwallposts/$', ProjectTextWallPostList.as_view(), name='project-textwallpost-list'),

)
