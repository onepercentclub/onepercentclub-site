from apps.projects.views import ManageProjectAmbassadortList, ManageProjectAmbassadorDetail
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
    surl(r'^pitches/<pk:#>$', ProjectPitchDetail.as_view(), name='project-pitch-detail'),
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


    url(r'^manage/$', ManageProjectList.as_view(), name='project-manage-list'),
    surl(r'^manage/<slug:s>$', ManageProjectDetail.as_view(), name='project-manage-detail'),
    surl(r'^manage/pitches/<pk:#>$', ManageProjectPitchDetail.as_view(), name='project-pitch-manage-detail'),
    surl(r'^manage/plans/<pk:#>$', ManageProjectPlanDetail.as_view(), name='project-plan-manage-detail'),


    url(r'^ambassadors/manage/$', ManageProjectAmbassadortList.as_view(), name='project-ambassador-manage-detail'),
    surl(r'^ambassadors/manage/<pk:#>$', ManageProjectAmbassadorDetail.as_view(), name='project-ambassador-manage-detail'),

)
