from django.conf.urls import patterns, url, include
from django.contrib.contenttypes.models import ContentType
from surlex.dj import surl
from .views import ProjectDetail, ProjectList
from .models import Project


urlpatterns = patterns('',
    url(r'^$', ProjectList.as_view(), name='project-list'),
    surl(r'^<slug:s>/wallposts/', include('apps.wallposts.urlsapi', namespace='wallposts'), {'content_type': ContentType.objects.get_for_model(Project).id}),
    url(r'^(?P<pk>[0-9]+)$', ProjectDetail.as_view(), name='project-detail'),
)
