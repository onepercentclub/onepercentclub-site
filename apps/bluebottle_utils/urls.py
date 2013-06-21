from django.conf.urls import patterns
from surlex.dj import surl
from .views import DocumentDownloadView

urlpatterns = patterns('',
    surl(r'^<content_type:#>/<pk:#>$', DocumentDownloadView.as_view(), name='document-download-detail'),
)
