from bluebottle.bb_accounts.serializers import UserPreviewSerializer
from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import (SorlImageField, SlugGenericRelatedField, PolymorphicSerializer, EuroField,
                                              TagSerializer, ImageSerializer, TaggableSerializerMixin)
from bluebottle.geo.models import Country
from bluebottle.utils.serializers import MetaField

from bluebottle.bb_projects.serializers import  ProjectThemeSerializer
from apps.fund.models import Donation

from bluebottle.utils.utils import get_project_model
from bluebottle.bb_projects.serializers import (ProjectSerializer as BaseProjectSerializer,
                                                ManageProjectSerializer as BaseManageProjectSerializer,
                                                ProjectPreviewSerializer as BaseProjectPreviewSerializer)

PROJECT_MODEL = get_project_model()


class ProjectCountrySerializer(serializers.ModelSerializer):

    subregion = serializers.CharField(source='subregion.name')

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectSerializer(BaseProjectSerializer):
    task_count = serializers.IntegerField(source='task_count')
    country = ProjectCountrySerializer(source='country')

    class Meta(BaseProjectSerializer):
        model = BaseProjectSerializer.Meta.model
        fields = BaseProjectSerializer.Meta.fields + ('task_count', 'amount_asked', 'amount_donated', 'amount_needed')


class ProjectPreviewSerializer(BaseProjectPreviewSerializer):
    task_count = serializers.IntegerField(source='task_count')

    class Meta(BaseProjectPreviewSerializer):
        model = BaseProjectPreviewSerializer.Meta.model
        fields = ('id', 'title', 'image', 'status', 'pitch', 'popularity', 'country', 'task_count',
                  'is_campaign', 'amount_asked', 'amount_donated', 'amount_needed', 'deadline')

class ManageProjectSerializer(BaseManageProjectSerializer):
    amount_asked = serializers.CharField(required=False)
    amount_donated = serializers.CharField(required=False)
    amount_needed = serializers.CharField(required=False)

    class Meta(BaseManageProjectSerializer):
        model = BaseManageProjectSerializer.Meta.model
        fields = BaseManageProjectSerializer.Meta.fields + ('amount_asked', 'amount_donated', 'amount_needed')

class ProjectSupporterSerializer(serializers.ModelSerializer):
    """
    For displaying donations on project and member pages.
    """
    member = UserPreviewSerializer(source='user')
    project = ProjectPreviewSerializer(source='project') # NOTE: is this really necessary?
    date_donated = serializers.DateTimeField(source='ready')

    class Meta:
        model = Donation
        fields = ('date_donated', 'project',  'member',)


class ProjectDonationSerializer(serializers.ModelSerializer):
    member = UserPreviewSerializer(source='user')
    date_donated = serializers.DateTimeField(source='ready')
    amount = EuroField(source='amount')

    class Meta:
        model = Donation
        fields = ('member', 'date_donated', 'amount',)


class ManageProjectSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source='slug', read_only=True)

    url = serializers.HyperlinkedIdentityField(view_name='project-manage-detail')
    status = serializers.CharField(read_only=True)

    pitch = serializers.PrimaryKeyRelatedField(source='projectpitch', read_only=True)
    plan = serializers.PrimaryKeyRelatedField(source='projectplan', read_only=True)
    campaign = serializers.PrimaryKeyRelatedField(source='projectcampaign', read_only=True)
    result = serializers.PrimaryKeyRelatedField(source='projectresult', read_only=True)

    coach = serializers.PrimaryKeyRelatedField(source='coach', read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'created', 'title', 'url', 'status', 'pitch', 'plan', 'campaign', 'coach')


# Serializers for ProjectWallPosts:

class ProjectTextWallPostSerializer(TextWallPostSerializer):
    """ TextWallPostSerializer with project specific customizations. """

    project = SlugGenericRelatedField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-textwallpost-detail')

    class Meta(TextWallPostSerializer.Meta):
        # Add the project slug field.
        fields = TextWallPostSerializer.Meta.fields + ('project',)

    def save(self, **kwargs):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        return super(ProjectTextWallPostSerializer, self).save(**kwargs)


class ProjectMediaWallPostSerializer(MediaWallPostSerializer):
    """ MediaWallPostSerializer with project specific customizations. """

    project = SlugGenericRelatedField(to_model=Project)
    url = serializers.HyperlinkedIdentityField(view_name='project-mediawallpost-detail')

    class Meta(MediaWallPostSerializer.Meta):
        # Add the project slug field.
        fields = MediaWallPostSerializer.Meta.fields + ('project',)

    def save(self, **kwargs):
        # Save the project content type on save.
        project_type = ContentType.objects.get_for_model(Project)
        self.object.content_type_id = project_type.id
        return super(ProjectMediaWallPostSerializer, self).save(**kwargs)


class ProjectWallPostSerializer(PolymorphicSerializer):
    """ Polymorphic WallPostSerializer with project specific customizations. """

    class Meta:
        child_models = (
            (TextWallPost, ProjectTextWallPostSerializer),
            (MediaWallPost, ProjectMediaWallPostSerializer),
        )


class ProjectThemeSerializer(serializers.ModelSerializer):
    title = serializers.Field(source='name')

    class Meta:
        model = ProjectTheme
        fields = ('id', 'title')
