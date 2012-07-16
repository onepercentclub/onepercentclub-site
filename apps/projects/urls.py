from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.projects.views',
    url(r'^view/(?P<slug>.+)/$', 'view'),
)

