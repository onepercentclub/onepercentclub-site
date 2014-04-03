from bluebottle.bb_accounts.serializers import UserPreviewSerializer
from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import (SorlImageField, SlugGenericRelatedField, PolymorphicSerializer, EuroField,
                                              TagSerializer, ImageSerializer, TaggableSerializerMixin)
from bluebottle.geo.models import Country
from bluebottle.utils.serializers import MetaField

from bluebottle.bb_projects.serializers import ProjectSerializer as BaseProjectSerializer, ProjectThemeSerializer
from apps.fund.models import Donation

from bluebottle.utils.utils import get_project_model

PROJECT_MODEL = get_project_model()


class ProjectCountrySerializer(serializers.ModelSerializer):

    subregion = serializers.CharField(source='subregion.name')

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectSerializer(BaseProjectSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    task_count = serializers.IntegerField(source='task_count')
    country = ProjectCountrySerializer(source='projectplan.country')

    meta_data = MetaField(
            title = 'get_meta_title',
            fb_title = 'get_fb_title',
            description = 'projectplan__pitch',
            keywords = 'projectplan__tags',
            image_source = 'projectplan__image',
            tweet = 'get_tweet',
            )

    def __init__(self, *args, **kwargs):
        super(ProjectSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = PROJECT_MODEL
        fields = BaseProjectSerializer.Meta.fields + ('task_count', 'amount_asked', 'amount_donated', 'amount_needed')


class ProjectPreviewSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    image = SorlImageField('image', '400x300', crop='center')
    country = ProjectCountrySerializer(source='country')
    pitch = serializers.CharField(source='pitch')

    task_count = serializers.IntegerField(source='task_count')

    class Meta:
        model = PROJECT_MODEL
        fields = ('id', 'title', 'image', 'status', 'pitch', 'popularity', 'country', 'task_count',
                  'is_campaign', 'amount_asked', 'amount_donated', 'amount_needed')


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

    class Meta:
        model = PROJECT_MODEL
        fields = ('id', 'created', 'title', 'url', 'status', 'pitch', 'plan', 'campaign', 'coach')

