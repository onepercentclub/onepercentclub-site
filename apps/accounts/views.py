from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import UserProfile


class UserProfileBase(object):
    queryset = UserProfile.objects.all().select_related('user')


class UserProfileList(UserProfileBase, ListView):
    pass


class UserProfileDetail(UserProfileBase, DetailView):
    pass
