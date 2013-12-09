from rest_framework import serializers
from apps.grouppages.models import GroupPage, GroupPageSlide
from apps.projects.serializers import ProjectPreviewSerializer
from bluebottle.accounts.serializers import UserPreviewSerializer


class GroupPageSlideSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupPageSlide


class GroupPageSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    members = UserPreviewSerializer(many=True)
    projects = ProjectPreviewSerializer(many=True)

    slides = GroupPageSlideSerializer(many=True, source='grouppageslide_set')

    class Meta:
        model = GroupPage