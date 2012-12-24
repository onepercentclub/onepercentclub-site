from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import RelatedField, ManyRelatedField, Field, HyperlinkedIdentityField
from apps.drf2serializers.serializers import SorlImageField
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


class ProjectSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = Field(source='get_language_display')
    organization = RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = Field(source='get_phase_display')
    tags = ManyRelatedField()
    url = HyperlinkedIdentityField(view_name='project-detail')
    money_asked = Field(source='money_asked')
    money_donated = Field(source='money_donated')
    image = SorlImageField('image', '800x450', crop='center')
    description = Field(source='description')

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization',
                  'owner', 'phase', 'planned_end_date', 'planned_start_date',
                  'slug', 'tags', 'themes', 'title', 'url', 'description')
