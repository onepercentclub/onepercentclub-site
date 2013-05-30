from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from rest_framework import generics
from django.utils.translation import ugettext_lazy as _
from .serializers import CurrentUserSerializer, UserProfileSerializer, UserSettingsSerializer, UserCreateSerializer
from .models import UserProfile
from .permissions import IsCurrentUser


# API views

class UserCreate(generics.CreateAPIView):
    model = User
    serializer_class = UserCreateSerializer


class UserProfileDetail(generics.RetrieveUpdateAPIView):
    model = User
    serializer_class = UserProfileSerializer


class UserSettingsDetail(generics.RetrieveUpdateAPIView):
    model = UserProfile
    serializer_class = UserSettingsSerializer
    permission_classes = (IsCurrentUser,)

    # FIXME: Remove this when we have a unified user model.
    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id', None)
        try:
            obj = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        self.check_object_permissions(self.request, obj)
        return obj.get_profile()


class CurrentUser(generics.RetrieveAPIView):
    model = User
    serializer_class = CurrentUserSerializer

    def get_object(self, queryset=None):
        """
        Override default to add support for object-level permissions.
        """
        if isinstance(self.request.user, AnonymousUser):
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.request.user
