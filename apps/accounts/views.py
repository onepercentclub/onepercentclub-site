from apps.accounts.models import BlueBottleUser
from apps.bluebottle_drf2.permissions import IsCurrentUserOrReadOnly, IsCurrentUser
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from rest_framework import generics
from django.utils.translation import ugettext_lazy as _
from .serializers import CurrentUserSerializer, UserProfileSerializer, UserSettingsSerializer, UserCreateSerializer


# API views

class UserCreate(generics.CreateAPIView):
    model = BlueBottleUser
    serializer_class = UserCreateSerializer


class UserProfileDetail(generics.RetrieveUpdateAPIView):
    model = BlueBottleUser
    serializer_class = UserProfileSerializer
    permission_classes = (IsCurrentUserOrReadOnly,)


class UserSettingsDetail(generics.RetrieveUpdateAPIView):
    model = BlueBottleUser
    serializer_class = UserSettingsSerializer
    permission_classes = (IsCurrentUser,)


class CurrentUser(generics.RetrieveAPIView):
    model = BlueBottleUser
    serializer_class = CurrentUserSerializer

    def get_object(self, queryset=None):
        """
        Override default to add support for object-level permissions.
        """
        if isinstance(self.request.user, AnonymousUser):
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.request.user
