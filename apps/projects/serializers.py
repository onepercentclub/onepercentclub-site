from apps.accounts.serializers import UserPreviewSerializer
from apps.fund.models import Donation
from apps.wallposts.models import TextWallPost, MediaWallPost
from apps.wallposts.serializers import TextWallPostSerializer, MediaWallPostSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from apps.bluebottle_drf2.serializers import SorlImageField, SlugGenericRelatedField, PolymorphicSerializer, EuroField
from apps.geo.models import Country
from .models import Project


class ProjectCountrySerializer(serializers.ModelSerializer):
    subregion = serializers.Field()

    class Meta:
        model = Country
        fields = ('name', 'subregion')


class ProjectPreviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    phase = serializers.CharField(source='get_phase_display', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    # country = ProjectCountrySerializer()
    money_asked = EuroField(source='money_asked')
    money_donated = EuroField(source='money_donated')
    image_square = SorlImageField('image', '120x120')

    class Meta:
        model = Project
        fields = ('id', 'country', 'image_square', 'money_asked', 'money_donated', 'phase', 'title', 'url')


class DonationPreviewSerializer(serializers.ModelSerializer):
    """
    For displaying donations on project and member pages.
    """
    member = UserPreviewSerializer(source='user')
    project = ProjectPreviewSerializer(source='project')
    date_donated = serializers.DateTimeField(source='created')

    class Meta:
        model = Donation
        fields = ('date_donated', 'project',  'member')


class ProjectSerializer(serializers.ModelSerializer):
    # Ember-data needs to have an unique id field for relationships to work. Normally it's the pk but in this case
    # it's the slug so we can display the project slug in the url.
    id = serializers.CharField(source='slug', read_only=True)
    # country = ProjectCountrySerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    language = serializers.CharField(source='get_language_display', read_only=True)
    organization = serializers.RelatedField()
    owner = UserPreviewSerializer()
    # TODO: This gets the display in English. How do we automatically switch to Dutch?
    phase = serializers.CharField(source='get_phase_display', read_only=True)
    tags = serializers.RelatedField(many=True)
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    money_asked = EuroField(source='money_asked')
    money_donated = EuroField(source='money_donated')
    image = SorlImageField('image', '800x450')
    image_bg = SorlImageField('image', '800x450', colorspace="GRAY")
    image_small = SorlImageField('image', '200x120')
    image_square = SorlImageField('image', '120x120')
    description = serializers.CharField(source='description', read_only=True)
    supporters_count = serializers.IntegerField(source='supporters_count', read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'country', 'created', 'image', 'image_small', 'image_square', 'image_bg', 'language', 'latitude',
                  'longitude', 'money_asked', 'money_donated', 'organization', 'owner', 'phase',
                  'planned_end_date', 'planned_start_date', 'tags', 'themes', 'title', 'url', 'description',
                  'supporters_count')


# Serializers for ProjectWallPosts:

class ProjectTextWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with project specific customizations. """

    project = SlugGenericRelatedField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-textwallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        # Add the project slug field.
        fields = TextWallPostSerializer.Meta.fields + ('project',)

    def save(self):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        return super(ProjectTextWallPostSerializer, self).save()


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    """ MediaWallPostSerializer with project specific customizations. """

    project = SlugGenericRelatedField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        # Add the project slug field.
        fields = MediaWallPostSerializer.Meta.fields + ('project',)

    def save(self):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        return super(ProjectMediaWallPostSerializer, self).save()


class ProjectWallPostSerializer(PolymorphicSerializer):
    """ Polymorphic WallPostSerializer with project specific customizations. """

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
        )
