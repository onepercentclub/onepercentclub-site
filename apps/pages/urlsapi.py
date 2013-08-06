from apps.pages.views import ContactRequestCreate
from django.conf.urls import patterns, url
from surlex.dj import surl
from .views import PageList, PageDetail

urlpatterns = patterns('',
    surl(r'^<language:s>/pages/$', PageList.as_view(), name='page-list'),
    surl(r'^<language:s>/pages/<slug:s>$', PageDetail.as_view(), name='page-detail'),
    url(r'^contact/$', ContactRequestCreate.as_view(), name='contact-request-create'),
)
