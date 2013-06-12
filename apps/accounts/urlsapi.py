from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import (UserProfileDetail, CurrentUser, UserSettingsDetail, UserCreate, UserActivate, PasswordReset,
                    PasswordSet)

# Public User API:
#
# User Create (POST):           /users/
# User Detail (GET/PUT):        /users/profiles/<pk>
# User Activate (GET):          /users/activate/<activation_key>
# User Password Reset (PUT):    /users/passwordreset
# User Password Set (PUT):      /users/passwordset/<uid36>-<token>
#
# Authenticated User API:
#
# Logged in user (GET):            /users/current
# User settings Detail (GET/PUT):  /users/settings/<pk>

urlpatterns = patterns('',
    url(r'^$', UserCreate.as_view(), name='user-user-create'),
    surl(r'^activate/<activation_key=[a-f0-9]{40}>$', UserActivate.as_view()),
    url(r'^current$', CurrentUser.as_view(), name='user-current'),
    url(r'^passwordreset$', PasswordReset.as_view(), name='password-reset'),
    surl(r'^passwordset/<uidb36=[0-9A-Za-z]{1,13}>-<token=[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}>$', PasswordSet.as_view(), name='password-set'),
    surl(r'^profiles/<pk:#>$', UserProfileDetail.as_view(), name='user-profile-detail'),
    surl(r'^settings/<pk:#>$', UserSettingsDetail.as_view(), name='user-settings-detail'),
)

