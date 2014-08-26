from bluebottle.bb_projects.serializers import ProjectPreviewSerializer
from bluebottle.quotes.serializers import QuoteSerializer
from bluebottle.slides.serializers import SlideSerializer

from apps.campaigns.serializers import CampaignSerializer
from apps.statistics.serializers import StatisticSerializer

from bluebottle.utils.serializer_dispatcher import get_serializer_class


from rest_framework import serializers


class HomePageSerializer(serializers.Serializer):
    quotes = QuoteSerializer(source='quotes')
    slides = SlideSerializer(source='slides')
    impact = StatisticSerializer(source='stats')
    projects = ProjectPreviewSerializer(source='projects')
    campaign = CampaignSerializer(source='campaign')
    fundraisers = get_serializer_class('FUNDRAISERS_FUNDRAISER_MODEL', 'preview')(source='fundraisers')
