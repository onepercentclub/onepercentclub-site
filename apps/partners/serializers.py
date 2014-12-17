from bluebottle.bluebottle_drf2.serializers import ImageSerializer
from bluebottle.projects.models import PartnerOrganization
from bluebottle.projects.serializers import ProjectSerializer, ProjectPreviewSerializer
from rest_framework import serializers


class PartnerOrganizationSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='slug', read_only=True)
    projects = ProjectPreviewSerializer(source='projects')
    description = serializers.CharField(source='description')
    image = ImageSerializer(required=False)

    class Meta:
        model = PartnerOrganization
        fields = ('id', 'name', 'projects', 'description', 'image')

