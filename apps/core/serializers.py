from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import EuroField, OEmbedField
from bluebottle.utils.model_dispatcher import get_donation_model
from bluebottle.bb_projects.serializers import ProjectSerializer as BaseProjectSerializer
from bluebottle.bb_fundraisers.serializers import BaseFundRaiserSerializer

from apps.members.serializers import UserProfileSerializer
from apps.projects.serializers import ProjectCountrySerializer, StoryField

DONATION_MODEL = get_donation_model()


class ProjectSerializer(BaseProjectSerializer):
    task_count = serializers.IntegerField(source='task_count')
    country = ProjectCountrySerializer(source='country')
    story = StoryField()
    video_html = OEmbedField(source='video_url', maxwidth='560', maxheight='315')
    partner = serializers.SlugRelatedField(slug_field='slug', source='partner_organization')

    class Meta(BaseProjectSerializer):
        model = BaseProjectSerializer.Meta.model
        fields = BaseProjectSerializer.Meta.fields + ('allow_overfunding', 'task_count', 'amount_asked', 'amount_donated', 'amount_needed',
                                                      'story', 'status', 'deadline', 'latitude', 'longitude', 'video_url', 'video_html', 'partner', 'mchanga_account')


class LatestDonationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    user = UserProfileSerializer()
    amount = EuroField()

    class Meta:
        model = DONATION_MODEL
        fields = ('id', 'project', 'fundraiser', 'user', 'created', 'anonymous', 'amount')