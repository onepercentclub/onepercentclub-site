from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import RelatedField, ManyRelatedField, Field
from apps.bluebottle_utils.serializers import SorlImageField, SlugHyperlinkedIdentityField
from apps.geo.models import Country
from .models import Project


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = Field()

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center', colorspace="GRAY")

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'picture')


class ProjectDetailSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = Field(source='get_language_display')
    organization = RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = Field(source='get_phase_display')
    tags = ManyRelatedField()
    url = SlugHyperlinkedIdentityField(view_name='project-instance')
    money_asked = Field(source='money_asked')
    money_donated = Field(source='money_donated')
    image = SorlImageField('image', '800x450', crop='center')
    description = Field(source='description')

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization',
                  'owner', 'phase', 'planned_end_date', 'planned_start_date',
                  'tags', 'themes', 'title', 'url', 'description')


class ProjectPreviewSerializer(ProjectDetailSerializer):
    image = SorlImageField('image', '230x150', crop='center')

    class Meta:
        model = Project
        fields = ('country', 'id', 'image', 'money_asked', 'money_donated',
                  'slug', 'title', 'url', 'phase')
