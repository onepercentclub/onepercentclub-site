from django.conf.urls import patterns, url, include
from surlex.dj import surl
from ..views import PartnerDetail

urlpatterns = patterns('',
    surl(r'^<slug:s>$', PartnerDetail.as_view(), name='partner-detail'),

)
