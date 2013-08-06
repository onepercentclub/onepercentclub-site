from apps.projects.models import PartnerOrganization
from apps.projects.serializers import ProjectSerializer, ProjectPreviewSerializer
from rest_framework import serializers


class PartnerOrganizationSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='slug', read_only=True)
    projects = ProjectPreviewSerializer(source='projects')

    class Meta:
        model = PartnerOrganization
        fields = ('id', 'name', 'projects')

