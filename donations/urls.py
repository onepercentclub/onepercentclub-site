from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('donations.views',
    url(r'^thanks/', 'thanks')
)

