from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from .views import HomeView


handler500 = 'bluebottle.views.handler500'

urlpatterns = i18n_patterns('',
    # These URL's will be automatically prefixed with the locale (e.g. '/nl/')
    url(r'^$', HomeView.as_view(), name='home'),

    # Django Admin, docs and password reset
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # account login/logout, password reset, and password change
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^projects/', include('apps.projects.urls')),

    # handlebar templates
    url(r'^templates/', include('apps.hbtemplates.urls'))
)

urlpatterns += patterns('',
    # Put your language-independent-views here

    # The api urls are in the /i18n/ url namespace so that they're not redirected to /en/
    url(r'^i18n/api/projects/', include('apps.projects.urlsapi')),

    # Needed for the self-documenting API in Django Rest Framework
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^i18n/', include('django.conf.urls.i18n')),
)

# Serve django-staticfiles (only works in DEBUG)
# https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()

# Serve media files (only works in DEBUG)
# https://docs.djangoproject.com/en/dev/howto/static-files/#django.conf.urls.static.static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
