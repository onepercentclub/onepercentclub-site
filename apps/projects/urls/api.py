from django.conf.urls import patterns, url, include
from surlex.dj import surl
from ..views import (ProjectDetail, ProjectList, ProjectSupporterList, ProjectDonationList)

urlpatterns = patterns('',
    url(r'^projects/$', ProjectList.as_view(), name='project-list'),
    surl(r'^projects/<slug:s>$', ProjectDetail.as_view(), name='project-detail'),

    # Project supporters
    url(r'^supporters/$', ProjectSupporterList.as_view(), name='project-supporter-list'),
    url(r'^donations/$', ProjectDonationList.as_view(), name='project-donation-list'),

)
