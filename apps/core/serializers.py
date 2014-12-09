from rest_framework import serializers

from bluebottle.bluebottle_drf2.serializers import EuroField, OEmbedField
from bluebottle.utils.model_dispatcher import get_donation_model
from bluebottle.bb_projects.serializers import (ProjectSerializer as BaseProjectSerializer,
												ProjectPreviewSerializer as BaseProjectPreviewSerializer)
from bluebottle.bb_fundraisers.serializers import BaseFundRaiserSerializer
from bluebottle.bb_accounts.serializers import UserPreviewSerializer

from apps.projects.serializers import ProjectCountrySerializer

DONATION_MODEL = get_donation_model()


class ProjectSerializer(BaseProjectPreviewSerializer):
    task_count = serializers.IntegerField(source='task_count')
    owner = UserPreviewSerializer(source='owner')
    partner = serializers.SlugRelatedField(slug_field='slug', source='partner_organization')

    class Meta(BaseProjectPreviewSerializer):
        model = BaseProjectPreviewSerializer.Meta.model
        fields = ('id', 'title', 'image', 'status', 'pitch', 'country', 'task_count', 'allow_overfunding',
                  'is_campaign', 'amount_asked', 'amount_donated', 'amount_needed', 'deadline', 'status', 'owner', 'partner')



class LatestDonationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    user = UserPreviewSerializer()
    amount = EuroField()

    class Meta:
        model = DONATION_MODEL
        fields = ('id', 'project', 'fundraiser', 'user', 'created', 'anonymous', 'amount')