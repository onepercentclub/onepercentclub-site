from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ReactionList, ReactionDetail

urlpatterns = patterns('',
    url(r'^$', ReactionList.as_view(), name='reaction-list'),
    url(r'^(?P<pk>[0-9]+)$', ReactionDetail.as_view(), name='reaction-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
