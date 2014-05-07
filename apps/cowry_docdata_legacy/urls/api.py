from django.conf.urls import patterns, url
from ..views import StatusChangedNotificationLegacyView

urlpatterns = patterns('',
    url(r'^$', StatusChangedNotificationLegacyView.as_view(), name='cowry-docdata-legacy-status-changed'),
)
