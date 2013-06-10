from apps.accounts.models import BlueBottleUser
from apps.bluebottle_drf2.permissions import IsCurrentUserOrReadOnly, IsCurrentUser
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from registration.models import RegistrationProfile
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from django.utils.translation import ugettext_lazy as _
from .serializers import CurrentUserSerializer, UserProfileSerializer, UserSettingsSerializer, UserCreateSerializer


# API views

class UserActivate(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        activation_key = self.kwargs.get('activation_key', None)
        activated_user = RegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            # Return 200 when the user has been activated. Could also log the user in at this point.
            # http://djangosnippets.org/snippets/1547/
            return response.Response(status=status.HTTP_200_OK)
        else:
            # Return 404 when the activation didn't work.
            return response.Response(status=status.HTTP_404_NOT_FOUND)


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
        if isinstance(self.request.user, AnonymousUser):
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.request.user
