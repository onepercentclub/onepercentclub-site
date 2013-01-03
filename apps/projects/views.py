from django.views.generic.detail import DetailView
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from .models import Project
from .serializers import ProjectSerializer


# API views

class ProjectList(generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)
    paginate_by = 10
    filter_fields = ('phase', 'slug')


class ProjectDetail(generics.RetrieveAPIView):
    model = Project
    serializer_class = ProjectSerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly,)


# Django template Views

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'
    
