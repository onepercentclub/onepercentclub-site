from apps.projects.views import ManageProjectAmbassadorList, ManageProjectAmbassadorDetail, ManageProjectBudgetLinetList, ManageProjectBudgetLineDetail
from django.conf.urls import patterns, url, include
from surlex.dj import surl
from .views import (ProjectDetail, ProjectList, ProjectWallPostList, ProjectWallPostDetail, ProjectMediaWallPostList,
                    ProjectMediaWallPostDetail, ProjectTextWallPostList, ProjectTextWallPostDetail,
                    ProjectMediaWallPostPhotoList, ProjectMediaWallPostPhotoDetail, ProjectDonationList,
                    ManageProjectList, ManageProjectDetail, ManageProjectPitchDetail, ManageProjectPlanDetail,
                    ProjectPitchDetail, ProjectPlanDetail)

urlpatterns = patterns('',
    url(r'^$', ProjectList.as_view(), name='project-list'),
    surl(r'^<slug:s>$', ProjectDetail.as_view(), name='project-detail'),
    # Not publically avaialable atm
    # surl(r'^pitches/<pk:#>$', ProjectPitchDetail.as_view(), name='project-pitch-detail'),
    surl(r'^plans/<pk:#>$', ProjectPlanDetail.as_view(), name='project-plan-detail'),


    # Project WallPost Urls
    url(r'^wallposts/$', ProjectWallPostList.as_view(), name='project-wallpost-list'),
    surl(r'^wallposts/<pk:#>$', ProjectWallPostDetail.as_view(), name='project-wallpost-detail'),
    url(r'^wallposts/media/$', ProjectMediaWallPostList.as_view(), name='project-mediawallpost-list'),
    surl(r'^wallposts/media/<pk:#>$', ProjectMediaWallPostDetail.as_view(), name='project-mediawallpost-detail'),
    url(r'^wallposts/text/$', ProjectTextWallPostList.as_view(), name='project-textwallpost-list'),
    surl(r'wallposts/text/<pk:#>$', ProjectTextWallPostDetail.as_view(), name='project-textwallpost-detail'),

    url(r'^wallposts/media/photos/$', ProjectMediaWallPostPhotoList.as_view(), name='project-mediawallpost-photo-list'),
    surl(r'^wallposts/media/photos/<pk:#>$', ProjectMediaWallPostPhotoDetail.as_view(), name='project-mediawallpost-photo-list'),

    # Project supporters
    url(r'^donations/$', ProjectDonationList.as_view(), name='project-donation-list'),

    # Manage stuff
    url(r'^manage/$', ManageProjectList.as_view(), name='project-manage-list'),
    surl(r'^manage/<slug:s>$', ManageProjectDetail.as_view(), name='project-manage-detail'),
    surl(r'^pitches/manage/<pk:#>$', ManageProjectPitchDetail.as_view(), name='project-pitch-manage-detail'),
    surl(r'^plans/manage/<pk:#>$', ManageProjectPlanDetail.as_view(), name='project-plan-manage-detail'),


    url(r'^ambassadors/manage/$', ManageProjectAmbassadorList.as_view(), name='project-ambassador-manage-detail'),
    surl(r'^ambassadors/manage/<pk:#>$', ManageProjectAmbassadorDetail.as_view(), name='project-ambassador-manage-detail'),

    url(r'^budgetlines/manage/$', ManageProjectBudgetLinetList.as_view(), name='project-budgetline-manage-detail'),
    surl(r'^budgetlines/manage/<pk:#>$', ManageProjectBudgetLineDetail.as_view(), name='project-budgetline-manage-detail'),

)
