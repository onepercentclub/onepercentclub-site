from django.conf.urls.defaults import patterns, url, include

from surlex.dj import surl

from .api import ProjectResource, ProjectMembersResource, IdeaPhaseResource
from .views import ProjectListView, ProjectDetailView, ProjectMapView, ProjectSearchView

project_resource = ProjectResource()
projectmembers_resource = ProjectMembersResource()
ideaphase_resource = IdeaPhaseResource()


urlpatterns = patterns('apps.projects.views',
    surl(r'^$', ProjectListView.as_view(), name='project_list'),
    surl(r'^search/$', ProjectSearchView.as_view(), name='project_search'),
    surl(r'^<slug:s>/$', ProjectDetailView.as_view(), name='project_detail'),
    surl(r'^<slug:s>/map/$', ProjectMapView.as_view(), name='project_map'),
)

# API urls
urlpatterns += patterns('',
    url(r'^api/', include(project_resource.urls)),
    url(r'^api/', include(projectmembers_resource.urls)),
    url(r'^api/', include(ideaphase_resource.urls)),
)
