from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import UserSettingsSerializer
from bluebottle.bluebottle_drf2.permissions import IsCurrentUser
from bluebottle.bb_accounts.views import UserSettingsDetail as BaseUserSettingsDetail

USER_MODEL = get_user_model


class UserSettingsDetail(BaseUserSettingsDetail):
    serializer_class = UserSettingsSerializer
