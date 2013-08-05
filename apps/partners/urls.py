from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import MacroMicroListView

urlpatterns = patterns('',
    url('macromicro/', MacroMicroListView.as_view(), name='macromicro-list')
)
