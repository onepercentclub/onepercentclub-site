from apps.projects.views import ManageProjectAmbassadorList, ManageProjectAmbassadorDetail, ManageProjectBudgetLinetList, ManageProjectBudgetLineDetail, ProjectPreviewList, ProjectPreviewDetail
from django.conf.urls import patterns, url, include
from surlex.dj import surl
from .views import (ProjectDetail, ProjectList, ProjectSupporterList,
                    ManageProjectList, ManageProjectDetail, ManageProjectPitchDetail, ManageProjectPlanDetail,
                    ProjectPitchDetail, ProjectPlanDetail, ManageProjectCampaignDetail, ProjectThemeList,
                    ProjectThemeDetail, ProjectDonationList)

urlpatterns = patterns('',
    url(r'^projects/$', ProjectList.as_view(), name='project-list'),
    surl(r'^projects/<slug:s>$', ProjectDetail.as_view(), name='project-detail'),

    url(r'^previews/$', ProjectPreviewList.as_view(), name='project-preview-list'),
    surl(r'^previews/<slug:s>$', ProjectPreviewDetail.as_view(), name='project-preview-detail'),

    # Not publically avaialable atm
    # surl(r'^pitches/<pk:#>$', ProjectPitchDetail.as_view(), name='project-pitch-detail'),
    surl(r'^plans/<pk:#>$', ProjectPlanDetail.as_view(), name='project-plan-detail'),

    surl(r'^themes/$', ProjectThemeList.as_view(), name='project-theme-list'),
    surl(r'^themes/<pk:#>$', ProjectThemeDetail.as_view(), name='project-theme-detail'),

    # Project supporters
    url(r'^supporters/$', ProjectSupporterList.as_view(), name='project-supporter-list'),
    url(r'^donations/$', ProjectDonationList.as_view(), name='project-donation-list'),

    # Manage stuff
    url(r'^manage/$', ManageProjectList.as_view(), name='project-manage-list'),
    surl(r'^manage/<slug:s>$', ManageProjectDetail.as_view(), name='project-manage-detail'),
    surl(r'^pitches/manage/<pk:#>$', ManageProjectPitchDetail.as_view(), name='project-pitch-manage-detail'),
    surl(r'^plans/manage/<pk:#>$', ManageProjectPlanDetail.as_view(), name='project-plan-manage-detail'),
    surl(r'^campaigns/manage/<pk:#>$', ManageProjectCampaignDetail.as_view(), name='project-campaign-manage-detail'),


    url(r'^ambassadors/manage/$', ManageProjectAmbassadorList.as_view(), name='project-ambassador-manage-detail'),
    surl(r'^ambassadors/manage/<pk:#>$', ManageProjectAmbassadorDetail.as_view(), name='project-ambassador-manage-detail'),

    url(r'^budgetlines/manage/$', ManageProjectBudgetLinetList.as_view(), name='project-budgetline-manage-detail'),
    surl(r'^budgetlines/manage/<pk:#>$', ManageProjectBudgetLineDetail.as_view(), name='project-budgetline-manage-detail'),

)
