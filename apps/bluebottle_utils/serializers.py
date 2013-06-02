from apps.projects.models import ProjectTheme
from rest_framework import serializers


class ThemeSerializer(serializers.ModelSerializer):
    title = serializers.Field(source='name')

    class Meta:
        model = ProjectTheme
        fields = ('id', 'title')