from django.conf.urls.defaults import patterns, url, include

from surlex.dj import surl

from .api import ProjectResource, ProjectDetailResource
from .views import ProjectListView, ProjectDetailView, ProjectMapView

project_resource = ProjectResource()
projectdetail_resource = ProjectDetailResource()


urlpatterns = patterns('apps.projects.views',
    surl(r'^$', ProjectListView.as_view(), name='project_list'),
    surl(r'^<slug:s>/$', ProjectDetailView.as_view(), name='project_detail'),
    surl(r'^<slug:s>/map/$', ProjectMapView.as_view(), name='project_map'),
)

# API urls
urlpatterns += patterns('',
    url(r'^api/', include(project_resource.urls)),
    url(r'^api/', include(projectdetail_resource.urls)),
)

