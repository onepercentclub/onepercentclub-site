from django.views.generic.detail import DetailView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from .models import Project
from .serializers import ProjectPreviewSerializer, ProjectDetailSerializer


# API views

class ProjectRoot(mixins.ListModelMixin,
                  generics.MultipleObjectBaseView):
    model = Project
    serializer_class = ProjectPreviewSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 4
    filter_fields = ('phase',)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProjectInstance(mixins.RetrieveModelMixin,
                      generics.SingleObjectBaseView):
    model = Project
    serializer_class = ProjectDetailSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# Django template Views

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'