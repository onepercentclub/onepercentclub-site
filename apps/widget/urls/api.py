from ..views import WidgetView
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url('^$', WidgetView.as_view(), name='partner-widget'),
)