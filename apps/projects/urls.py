from django.conf.urls.defaults import patterns, url, include

from surlex.dj import surl

from .views import ProjectListView, ProjectDetailView, ProjectMapView

urlpatterns = patterns('apps.projects.views',
    surl(r'^$', ProjectListView.as_view(), name='project_list'),
    surl(r'^<slug:s>/$', ProjectDetailView.as_view(), name='project_detail'),
    surl(r'^<slug:s>/map/$', ProjectMapView.as_view(), name='project_map'),
)

