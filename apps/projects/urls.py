from django.conf.urls.defaults import patterns
from surlex.dj import surl

from .views import ProjectListView, ProjectDetailView


urlpatterns = patterns('',
    surl(r'^$', ProjectListView.as_view(), name='project_list'),
    surl(r'^<slug:s>/$', ProjectDetailView.as_view(), name='project_detail'),
)

