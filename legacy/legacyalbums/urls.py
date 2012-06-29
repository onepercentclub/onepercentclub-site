from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('legacyalbums.views',
    url(r'^view/', 'thanks')
)

