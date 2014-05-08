from apps.projects.models import ProjectBudgetLine
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

from bs4 import BeautifulSoup

PROJECT_MODEL = get_project_model()

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



class ProjectCountrySerializer(serializers.ModelSerializer):

    subregion = serializers.CharField(source='subregion.name')

    class Meta:
        model = Country
        fields = ('id', 'name', 'subregion')


class ProjectSerializer(BaseProjectSerializer):
    task_count = serializers.IntegerField(source='task_count')
    country = ProjectCountrySerializer(source='country')
    story = StoryField()

    class Meta(BaseProjectSerializer):
        model = BaseProjectSerializer.Meta.model
        fields = BaseProjectSerializer.Meta.fields + ('task_count', 'amount_asked', 'amount_donated', 'amount_needed',
                                                      'story', 'status', 'deadline', 'latitude', 'longitude')


class ProjectPreviewSerializer(BaseProjectPreviewSerializer):
    task_count = serializers.IntegerField(source='task_count')

    class Meta(BaseProjectPreviewSerializer):
        model = BaseProjectPreviewSerializer.Meta.model
        fields = ('id', 'title', 'image', 'status', 'pitch', 'popularity', 'country', 'task_count',
                  'is_campaign', 'amount_asked', 'amount_donated', 'amount_needed', 'deadline', 'status')


class ProjectBudgetLineSerializer(serializers.ModelSerializer):

    amount = EuroField()
    project = serializers.SlugRelatedField(slug_field='slug')

    class Meta:
        model = ProjectBudgetLine
        fields = ('id', 'project', 'description', 'amount')


class ManageProjectSerializer(BaseManageProjectSerializer):
    amount_asked = serializers.CharField(required=False)
    amount_donated = serializers.CharField(read_only=True)
    amount_needed = serializers.CharField(read_only=True)
    budget_lines = ProjectBudgetLineSerializer(many=True, source='projectbudgetline_set', read_only=True)

    story = StoryField(required=False)

    class Meta(BaseManageProjectSerializer):
        model = BaseManageProjectSerializer.Meta.model
        fields = BaseManageProjectSerializer.Meta.fields + ('amount_asked', 'amount_donated', 'amount_needed',
                                                            'story', 'budget_lines', 'deadline', 'latitude', 'longitude')

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

