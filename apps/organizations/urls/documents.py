from django.conf.urls import patterns
from surlex.dj import surl
from ..views import RegistrationDocumentDownloadView

urlpatterns = patterns('',
    surl(r'^organizations/<pk:#>/$', RegistrationDocumentDownloadView.as_view(), name='organization-registration-download'),
)
