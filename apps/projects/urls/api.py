from apps.projects.views import ProjectPreviewList, ProjectPreviewDetail
from django.conf.urls import patterns, url, include
from surlex.dj import surl
from ..views import (ProjectDetail, ProjectList, ProjectSupporterList, ProjectDonationList)

urlpatterns = patterns('',
    url(r'^projects/$', ProjectList.as_view(), name='project-list'),
    surl(r'^projects/<slug:s>$', ProjectDetail.as_view(), name='project-detail'),

    url(r'^previews/$', ProjectPreviewList.as_view(), name='project-preview-list'),
    surl(r'^previews/<slug:s>$', ProjectPreviewDetail.as_view(), name='project-preview-detail'),

    # Project supporters
    url(r'^supporters/$', ProjectSupporterList.as_view(), name='project-supporter-list'),
    url(r'^donations/$', ProjectDonationList.as_view(), name='project-donation-list'),

)
