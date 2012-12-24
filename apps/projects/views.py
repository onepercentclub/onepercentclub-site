from django.views.generic.detail import DetailView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from .models import Project
from .serializers import ProjectSerializer


# API views

class ProjectList(mixins.ListModelMixin,
                  generics.MultipleObjectAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    filter_fields = ('phase', 'slug')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ProjectDetail(mixins.RetrieveModelMixin,
                    generics.SingleObjectAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# Django template Views

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'