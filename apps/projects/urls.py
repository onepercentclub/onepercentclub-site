from django.conf.urls import patterns
from surlex.dj import surl
from .views import ProjectDetailView

urlpatterns = patterns('',
    surl(r'^<slug:s>$', ProjectDetailView.as_view(), name='project-detail'),
    #surl('/macromicro/xml', MacroMicroListView.as_view(), name='macromicro-project-list')
)
