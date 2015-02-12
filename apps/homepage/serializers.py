from bluebottle.bb_projects.serializers import ProjectPreviewSerializer
from bluebottle.quotes.serializers import QuoteSerializer
from bluebottle.slides.serializers import SlideSerializer

from apps.campaigns.serializers import CampaignSerializer
from bluebottle.bb_fundraisers.serializers import BaseFundRaiserSerializer
from apps.statistics.serializers import StatisticSerializer



from rest_framework import serializers


class HomePageSerializer(serializers.Serializer):
    quotes = QuoteSerializer(source='quotes')
    slides = SlideSerializer(source='slides')
    impact = StatisticSerializer(source='stats')
    projects = ProjectPreviewSerializer(source='projects')
    campaign = CampaignSerializer(source='campaign')
    fundraisers = BaseFundRaiserSerializer(source='fundraisers')
