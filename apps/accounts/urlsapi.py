from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import UserProfileDetail, CurrentUser, UserSettingsDetail, UserCreate

# Public User API:
#
# User Create (POST):      /users/
# User Detail (GET/PUT):   /users/profiles/<pk>
#
# Authenticated User API:
#
# Logged in user (GET):            /users/current
# User settings Detail (GET/PUT):  /users/settings/<pk>

urlpatterns = patterns('',
    url(r'^$', UserCreate.as_view(), name='user-user-create'),
    surl(r'^profiles/<pk:#>$', UserProfileDetail.as_view(), name='user-profile-detail'),
    url(r'^current$', CurrentUser.as_view(), name='user-current'),
    surl(r'^settings/<pk:#>$', UserSettingsDetail.as_view(), name='user-settings-detail'),
)
