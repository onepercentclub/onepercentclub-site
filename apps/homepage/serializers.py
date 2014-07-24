from bluebottle.quotes.serializers import QuoteSerializer
from bluebottle.slides.serializers import SlideSerializer
from bluebottle.utils.utils import get_serializer_class

from apps.campaigns.serializers import CampaignSerializer
from apps.statistics.serializers import StatisticSerializer



from rest_framework import serializers


class HomePageSerializer(serializers.Serializer):
    quotes = QuoteSerializer(source='quotes')
    slides = SlideSerializer(source='slides')
    impact = StatisticSerializer(source='stats')
    projects = get_serializer_class('PROJECTS_PROJECT_MODEL', 'preview')(source='projects')
    campaign = CampaignSerializer(source='campaign')
    fundraisers = get_serializer_class('FUNDRAISERS_FUNDRAISER_MODEL', 'preview')(source='fundraisers')
