from django.conf.urls import patterns, url
from surlex.dj import surl
from ..views import MacroMicroListView

urlpatterns = patterns('',
    url('macromicro/xml', MacroMicroListView.as_view(), name='macromicro-list')
)
