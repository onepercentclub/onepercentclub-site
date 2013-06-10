from apps.accounts.serializers import UserPreviewSerializer
from apps.fund.models import Donation
from apps.projects.models import ProjectPitch, ProjectPlan
from apps.wallposts.models import TextWallPost, MediaWallPost
from apps.wallposts.serializers import TextWallPostSerializer, MediaWallPostSerializer, WallPostListSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from apps.bluebottle_drf2.serializers import SorlImageField, SlugGenericRelatedField, PolymorphicSerializer, EuroField, TaggableSerializerMixin, TagSerializer
from apps.geo.models import Country
from .models import Project


class ProjectCountrySerializer(serializers.ModelSerializer):

    subregion = serializers.CharField(source='subregion.name')

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectPreviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    phase = serializers.CharField(source='get_phase_display', read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='project-detail')
    country = ProjectCountrySerializer(source='pitch.country')
    money_asked = EuroField(source='money_asked')
    money_donated = EuroField(source='money_donated')
    image_square = SorlImageField('image', '120x120')

    class Meta:
        model = Project
        fields = ('id', 'phase', 'title', 'url', 'money_donated', 'money_asked')


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


class ProjectPitchSerializer(serializers.ModelSerializer):

    country = ProjectCountrySerializer()
    theme = serializers.PrimaryKeyRelatedField()
    tags = TagSerializer()

    image = SorlImageField('image', '800x450', required=False)
    image_bg = SorlImageField('image', '800x450', colorspace="GRAY", read_only=True)
    image_small = SorlImageField('image', '200x120', read_only=True)
    image_square = SorlImageField('image', '120x120', read_only=True)

    class Meta:
        model = ProjectPitch
        fields = ('id', 'title', 'pitch', 'theme', 'tags', 'description', 'country', 'latitude', 'longitude', 'need',
                  'status', 'image', 'image_bg', 'image_small', 'image_square')


class ManageProjectPitchSerializer(TaggableSerializerMixin, ProjectPitchSerializer):

    country = serializers.PrimaryKeyRelatedField(required=False)

    def validate_status(self, attrs, source):
        value = attrs[source]
        if value not in [ProjectPitch.PitchStatuses.submitted, ProjectPitch.PitchStatuses.new]:
            raise serializers.ValidationError("You can only change status into 'submitted'")
        return attrs


class ProjectPlanSerializer(serializers.ModelSerializer):

    country = ProjectCountrySerializer()
    theme = serializers.PrimaryKeyRelatedField()
    tags = TagSerializer()
    organization = serializers.PrimaryKeyRelatedField(source="organization")

    image = SorlImageField('image', '800x450', required=False)
    image_bg = SorlImageField('image', '800x450', colorspace="GRAY", read_only=True)
    image_small = SorlImageField('image', '200x120', read_only=True)
    image_square = SorlImageField('image', '120x120', read_only=True)

    class Meta:
        model = ProjectPlan
        fields = ('id', 'title', 'pitch', 'theme', 'tags', 'description', 'country', 'latitude', 'longitude', 'need',
                  'status', 'image', 'image_bg', 'image_small', 'image_square', 'organization')


class ManageProjectPlanSerializer(TaggableSerializerMixin, ProjectPlanSerializer):

    country = serializers.PrimaryKeyRelatedField(required=False)


    def validate_status(self, attrs, source):
        value = attrs[source]
        if value not in [ProjectPitch.PitchStatuses.submitted, ProjectPitch.PitchStatuses.new]:
            raise serializers.ValidationError("You can only change status into 'submitted'")
        return attrs


class ManageProjectSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='slug', read_only=True)

    url = serializers.HyperlinkedIdentityField(view_name='project-manage-detail')
    phase = serializers.CharField(read_only=True)

    pitch = serializers.PrimaryKeyRelatedField(source='projectpitch', null=True, read_only=True)
    plan = serializers.PrimaryKeyRelatedField(source='projectplan', null=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'created', 'title', 'url', 'phase', 'pitch', 'plan')


class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)

    owner = UserPreviewSerializer()
    team_member = UserPreviewSerializer()

    money_asked = EuroField(source='money_asked')
    money_donated = EuroField(source='money_donated')

    pitch = serializers.PrimaryKeyRelatedField(source='projectpitch', null=True, read_only=True)
    plan = serializers.PrimaryKeyRelatedField(source='projectplan', null=True, read_only=True)

    wallpost_ids = WallPostListSerializer()

    class Meta:
        model = Project
        fields = ('id', 'created', 'title', 'money_donated', 'money_asked', 'owner', 'team_member', 'pitch', 'plan', 'wallpost_ids')


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


