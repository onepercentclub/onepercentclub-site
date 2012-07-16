from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from .views import HomeView


# Serve django-staticfiles (only works in DEBUG)
urlpatterns = staticfiles_urlpatterns()

# Serve media files (only works in DEBUG)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.GLOBAL_URL, document_root=settings.GLOBAL_ROOT)



handler500 = 'bluebottle.views.handler500'


urlpatterns += patterns('',
    url(r'^$', HomeView.as_view(), name='home'),

    # Django Admin, docs and password reset
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    (r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    # account login/logout, password reset, and password change
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^projects/', include('apps.projects.urls')),

)

