# TODO: Do we still need this?
from django.conf.urls import patterns
from surlex.dj import surl
from ..views import ProjectDetailView, ProjectIframeView

urlpatterns = patterns('',
    surl(r'^<slug:s>$', ProjectDetailView.as_view(), name='project-detail'),
    surl(r'^<slug:s>/iframe/$', ProjectIframeView.as_view(), name='project-iframe'),
)
