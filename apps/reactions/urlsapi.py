from django.conf.urls import patterns, url
from .views import ReactionList, ReactionDetail

urlpatterns = patterns('reactions',
    url(r'^$', ReactionList.as_view(), name='reaction-list'),
    url(r'^(?P<pk>[0-9]+)$', ReactionDetail.as_view(), name='reaction-detail'),
)
