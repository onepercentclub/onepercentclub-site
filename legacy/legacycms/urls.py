from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('legacycms.views',
    url(r'^overview/', 'overview'),
    url(r'^view/(?P<id>.+)/$', 'view'),
)

