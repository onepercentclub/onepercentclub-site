from apps.organizations.views import ManageOrganizationList, ManageOrganizationDetail
from django.conf.urls import patterns, url, include
from surlex.dj import surl
from .views import OrganizationDetail, OrganizationList

urlpatterns = patterns('',
    url(r'^$', OrganizationList.as_view(), name='organization-list'),
    surl(r'^<pk:#>$', OrganizationDetail.as_view(), name='organization-detail'),
    surl(r'^manage/$', ManageOrganizationList.as_view(), name='manage-organization-list'),
    surl(r'^manage/<pk:#>$', ManageOrganizationDetail.as_view(), name='manage-organization-detail'),
)
