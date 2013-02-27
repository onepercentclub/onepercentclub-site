from django.contrib.auth.models import User
from rest_framework import serializers
from apps.bluebottle_drf2.serializers import SorlImageField
from apps.geo.models import Country
from .models import Project


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = serializers.Field()

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture', 'username')


class ProjectSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = serializers.CharField(source='get_language_display', read_only=True)
    organization = serializers.RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = serializers.CharField(source='get_phase_display', read_only=True)
    tags = serializers.RelatedField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    money_asked = serializers.Field(source='money_asked')
    money_donated = serializers.Field(source='money_donated')
    image = SorlImageField('image', '800x450')
    image_small = SorlImageField('image', '200x120')
    image_square = SorlImageField('image', '120x120')
    description = serializers.CharField(source='description', read_only=True)

    class Meta:
        model = Project
        fields = ('country', 'created', 'image', 'image_small', 'image_square', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization',
                  'owner', 'phase', 'planned_end_date', 'planned_start_date',
                  'slug', 'tags', 'themes', 'title', 'url', 'description')
