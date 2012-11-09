from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from rest_framework import generics
from .serializers import MemberListSerializer, MemberDetailSerializer
from .models import UserProfile


# API views

class MemberList(generics.ListAPIView):
    model = User
    serializer_class = MemberListSerializer
    paginate_by = 10


class MemberDetail(generics.RetrieveAPIView):
    model = User
    serializer_class = MemberDetailSerializer

class MemberCurrent(generics.RetrieveAPIView):
    model = User
    serializer_class = MemberDetailSerializer
            
    def get_object(self):
        """
        Override default to add support for object-level permissions.
        """
        if self.request.user:
            user = User.objects.filter(pk=self.request.user.id).get()
            return user
        return None


# Django template Views

class UserProfileBase(object):
    queryset = UserProfile.objects.all().select_related('user')


class UserProfileList(UserProfileBase, ListView):
    pass


class UserProfileDetail(UserProfileBase, DetailView):
    pass
