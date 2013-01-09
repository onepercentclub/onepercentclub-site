from django.contrib.auth.models import User
from rest_framework import serializers
from apps.drf2serializers.serializers import SorlImageField
from apps.bluebottle_drf2.serializers import SorlImageField
from apps.geo.models import Country
from .models import Project


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = serializers.Field()

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture', 'username')


class ProjectSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = serializers.Field(source='get_language_display')
    organization = serializers.RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = serializers.Field(source='get_phase_display')
    tags = serializers.ManyRelatedField()
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    money_asked = serializers.Field(source='money_asked')
    money_donated = serializers.Field(source='money_donated')
    image = SorlImageField('image', '800x450', crop='center')
    description = serializers.Field(source='description')

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization',
                  'owner', 'phase', 'planned_end_date', 'planned_start_date',
                  'slug', 'tags', 'themes', 'title', 'url', 'description')
