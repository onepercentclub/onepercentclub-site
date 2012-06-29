from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('legacydonations.views',
    url(r'^thanks/', 'thanks')
)

