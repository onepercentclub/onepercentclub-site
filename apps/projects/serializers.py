from apps.projects.models import ProjectBudgetLine
from bluebottle.bb_accounts.serializers import UserPreviewSerializer
from bluebottle.geo.serializers import CountrySerializer
from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import EuroField
from bluebottle.geo.models import Country
from bluebottle.bluebottle_drf2.serializers import OEmbedField
from bluebottle.utils.model_dispatcher import get_project_model, get_donation_model
from bluebottle.bb_projects.serializers import (ProjectSerializer as BaseProjectSerializer,
                                                ManageProjectSerializer as BaseManageProjectSerializer,
                                                ProjectPreviewSerializer as BaseProjectPreviewSerializer)

from bs4 import BeautifulSoup

PROJECT_MODEL = get_project_model()
DONATION_MODEL = get_donation_model()


class StoryField(serializers.WritableField):
    def to_native(self, value):
        """ Reading / Loading the story field """
        return value

    def from_native(self, data):
        """ Saving the story text """
        #Convert &gt; and &lt; back to HTML tags so Beautiful Soup can clean unwanted tags.
        #Script tags are sent by redactor as "&lt;;script&gt;;", Iframe tags have just one semicolon.
        data = data.replace("&lt;;", "<").replace("&gt;;", ">").replace("&lt;", "<").replace("&gt;", ">")
        soup = BeautifulSoup(data, "html.parser")
        [s.extract() for s in soup(['script', 'iframe'])]
        return str(soup)


class ProjectCountrySerializer(CountrySerializer):

    subregion = serializers.CharField(source='subregion.name')

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion', 'code')


class ProjectSerializer(BaseProjectSerializer):
    task_count = serializers.IntegerField(source='task_count')
    country = ProjectCountrySerializer(source='country')
    story = StoryField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')

    class Meta(BaseProjectSerializer):
        model = BaseProjectSerializer.Meta.model
        fields = BaseProjectSerializer.Meta.fields + ('allow_overfunding', 'task_count', 'amount_asked', 'amount_donated', 'amount_needed',
                                                      'story', 'status', 'deadline', 'latitude', 'longitude', 'video_url', 'video_html')


class ProjectPreviewSerializer(BaseProjectPreviewSerializer):
    task_count = serializers.IntegerField(source='task_count')
    owner = UserPreviewSerializer(source='owner')

    class Meta(BaseProjectPreviewSerializer):
        model = BaseProjectPreviewSerializer.Meta.model
        fields = ('id', 'title', 'image', 'status', 'pitch', 'country', 'task_count',
                  'is_campaign', 'amount_asked', 'amount_donated', 'amount_needed', 'deadline', 'status', 'owner')


class ProjectBudgetLineSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(slug_field='slug')

    class Meta:
        model = ProjectBudgetLine
        fields = ('id', 'project', 'description', 'amount')


class ManageProjectSerializer(BaseManageProjectSerializer):
    amount_asked = serializers.CharField(required=False)
    amount_donated = serializers.CharField(read_only=True)
    amount_needed = serializers.CharField(read_only=True)
    budget_lines = ProjectBudgetLineSerializer(many=True, source='projectbudgetline_set', read_only=True)
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    story = StoryField(required=False)

    class Meta(BaseManageProjectSerializer):
        model = BaseManageProjectSerializer.Meta.model
        fields = BaseManageProjectSerializer.Meta.fields + ('amount_asked', 'amount_donated', 'amount_needed',
                                                            'video_url', 'video_html',
                                                            'story', 'budget_lines', 'deadline', 'latitude', 'longitude')


class ProjectSupporterSerializer(serializers.ModelSerializer):
    """
    For displaying donations on project and member pages.
    """
    member = UserPreviewSerializer(source='user')
    project = ProjectPreviewSerializer(source='project') # NOTE: is this really necessary?
    date_donated = serializers.DateTimeField(source='ready')

    class Meta:
        model = DONATION_MODEL
        fields = ('date_donated', 'project',  'member',)


class ProjectDonationSerializer(serializers.ModelSerializer):
    member = UserPreviewSerializer(source='user')
    date_donated = serializers.DateTimeField(source='ready')

    class Meta:
        model = DONATION_MODEL
        fields = ('member', 'date_donated', 'amount',)

