from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.fields import RelatedField, ManyRelatedField, Field, HyperlinkedIdentityField
from rest_framework import fields
from apps.bluebottle_drf2.serializers import SorlImageField, PolymorphicSerializer
from apps.geo.models import Country
from apps.wallposts.serializers import MediaWallPostSerializer, TextWallPostSerializer, ObjectIdField
from apps.wallposts.models import MediaWallPost, TextWallPost
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
        fields = ('id', 'first_name', 'last_name', 'picture', 'username')


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



# Project WallPost Serializers


class ProjectTextWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with project specific customizations. """

    project_id = ObjectIdField(model=TextWallPost, to_model=Project)
    url = fields.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        # Add the project_id field.
        fields = TextWallPostSerializer.Meta.fields + ('project_id',)

    def save(self, save_m2m=True):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectTextWallPostSerializer, self).save(save_m2m)


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    """ MediaWallPostSerializer with project specific customizations. """

    project_id = ObjectIdField(model=MediaWallPost, to_model=Project)
    url = fields.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        # Add the project_id field.
        fields = MediaWallPostSerializer.Meta.fields + ('project_id',)

    def save(self, save_m2m=True):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        super(ProjectMediaWallPostSerializer, self).save(save_m2m)


class ProjectWallPostSerializer(PolymorphicSerializer):
    """ Polymorphic WallPostSerializer with project specific customizations. """

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
            )
