from apps.projects.models import PartnerOrganization
from rest_framework import serializers


class PartnerOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerOrganization
        fields = ('id', 'name', 'projects')

