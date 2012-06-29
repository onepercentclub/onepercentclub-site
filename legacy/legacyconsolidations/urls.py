from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('legacyconsolidations.views',
    url(r'^overview/', 'overview'),
    url(r'^settlement/(?P<id>.+)/$', 'settlement'),
)

