from django.conf.urls import patterns
from surlex.dj import surl
from .views import OrganizationDocumentDownloadView

urlpatterns = patterns('',
    surl(r'^documents/<pk:#>$', OrganizationDocumentDownloadView.as_view(), name='organization-document-download-detail'),
)
