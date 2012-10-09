from apps.geo.models import Country
from django.conf import settings
from django.contrib.auth.models import User
from .models import Project
from rest_framework import serializers
from rest_framework.fields import CharField, RelatedField, ManyRelatedField, Field
from sorl.thumbnail.shortcuts import get_thumbnail


# TODO move this to utils class
class SorlImageField(Field):

    def __init__(self, source, geometry_string, **options):
        super(SorlImageField, self).__init__(source)
        self.geometry_string = geometry_string
        self.options = options

    def to_native(self, value):
        if value:
            return settings.MEDIA_URL + \
                   unicode(get_thumbnail(value, self.geometry_string, **self.options))
        else:
            return ""


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = RelatedField()

    class Meta:
        model = Country
        fields = ('name', 'subregion')


class ProjectOwnerSerializer(serializers.ModelSerializer):
    picture = SorlImageField('userprofile.picture', '90x90', crop='center')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'picture')


class ProjectDetailSerializer(serializers.ModelSerializer):
    country = ProjectCountrySerializer()
    image = SorlImageField('image', '480x360', fit='center')
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = Field(source='get_language_display')
    organization = RelatedField()
    owner = ProjectOwnerSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = Field(source='get_phase_display')
    tags = ManyRelatedField()
    url = CharField(source='get_absolute_url', readonly=True)

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language',
                  'latitude', 'longitude', 'organization', 'owner', 'phase',
                  'planned_end_date', 'planned_start_date', 'slug', 'tags',
                  'themes', 'title', 'url')


class ProjectPreviewSerializer(ProjectDetailSerializer):
    image = SorlImageField('image', '225x150', crop='center')

    class Meta:
        model = Project
        fields = ('country', 'created', 'id', 'image', 'language',
                  'latitude', 'longitude', 'organization', 'phase', 'slug',
                  'title', 'url')
