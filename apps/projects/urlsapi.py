from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from surlex.dj import surl
from .views import ProjectDetail, ProjectList

urlpatterns = patterns('',
    url(r'^$', ProjectList.as_view(), name='project-list'),
    surl(r'^<slug:s>$', ProjectDetail.as_view(), name='project-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
