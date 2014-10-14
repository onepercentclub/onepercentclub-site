from django.conf.urls import patterns, url
from ..views import WidgetView

urlpatterns = patterns('',
	url('^$', WidgetView.as_view(), name='widget')
)