from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from rest_framework import generics
from django.utils.translation import ugettext_lazy as _
from .serializers import (MemberSerializer, AuthenticatedUserSerializer,  MemberProfileSerializer,
                          MemberSettingsSerializer, UserCreationSerializer)
from .models import UserProfile
from .permissions import IsCurrentUser


# API views

class UserCreation(generics.CreateAPIView):
    model = User
    serializer_class = UserCreationSerializer


class MemberList(generics.ListAPIView):
    model = User
    serializer_class = MemberSerializer
    paginate_by = 10


class MemberProfileDetail(generics.RetrieveAPIView):
    model = User
    serializer_class = MemberProfileSerializer


class MemberSettingsDetail(generics.RetrieveUpdateAPIView):
    model = UserProfile
    serializer_class = MemberSettingsSerializer
    permission_classes = (IsCurrentUser,)

    def get_object(self, queryset=None):
        """
        """
        username = self.kwargs.get('username', None)
        try:
            obj = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        self.check_object_permissions(self.request, obj)
        return obj.get_profile()


class AuthenticatedUser(generics.RetrieveAPIView):
    model = User
    serializer_class = AuthenticatedUserSerializer

    def get_object(self, queryset=None):
        """
        Override default to add support for object-level permissions.
        """

        if isinstance(self.request.user, AnonymousUser):
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.request.user


# Django template Views

class UserProfileBase(object):
    queryset = UserProfile.objects.all().select_related('user')


class UserProfileList(UserProfileBase, ListView):
    pass


class UserProfileDetail(UserProfileBase, DetailView):
    pass
