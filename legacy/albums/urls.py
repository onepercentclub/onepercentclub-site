from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('albums.views',
    url(r'^view/', 'thanks')
)

