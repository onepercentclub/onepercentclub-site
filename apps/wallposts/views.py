from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from rest_framework import mixins
from apps.projects.models import Project
from .serializers import WallPostSerializer, ProjectWallPostSerializer
from .models import WallPost


class WallPostList(generics.ListAPIView):
    # Please extend this. We probably don't want to use this directly. 
    model = WallPost
    serializer_class = WallPostSerializer
    paginate_by = 10

    def get_content_type(self):
        # Have a separate function for this so we can easily
        # overwrite it for specific wallpost APIs
        return self.request.QUERY_PARAMS.get('content_type', None)

    def get_object_id(self):
        return self.request.QUERY_PARAMS.get('object_id', None)

    def get_queryset(self):
        objects = self.model.objects
        if self.get_content_type():
            objects = objects.for_content_type(self.get_content_type())
        if self.get_object_id():
            # TODO: We should really throw a warning if content_type is not set here.
            objects = objects.filter(object_id=self.get_object_id())
        objects = objects.order_by("-created")
        return objects


class WallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = WallPostSerializer


# Views specific to the ProjectWallPosts:

class ProjectWallPostList(WallPostList):
    serializer_class = ProjectWallPostSerializer

    def get_content_type(self):
        return ContentType.objects.get_for_model(Project).id

    def get_object_id(self):
        # We want to be specific and use project_id here.
        # Note: We're not using the filter_fields auto-filter generation because 'project_id' is not defined on the model
        # and therefore doesn't work. This could be a bug in the DRF2 auto-filter support.
        return self.request.QUERY_PARAMS.get('project_id', None)


class ProjectWallPostDetail(generics.RetrieveAPIView):
    model = WallPost
    serializer_class = ProjectWallPostSerializer

    def get_queryset(self):
        project_type = ContentType.objects.get_for_model(Project)
        return self.model.objects.filter(content_type__pk=project_type.id)
