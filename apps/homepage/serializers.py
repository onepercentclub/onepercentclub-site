from apps.banners.serializers import SlideSerializer
from apps.campaigns.serializers import CampaignSerializer
from apps.fundraisers.serializers import FundRaiserSerializer
from apps.projects.serializers import ProjectPreviewSerializer
from apps.quotes.serializers import QuoteSerializer
from apps.statistics.serializers import StatisticSerializer

from rest_framework import serializers


class HomePageSerializer(serializers.Serializer):
    quotes = QuoteSerializer(source='quotes')
    slides = SlideSerializer(source='slides')
    impact = StatisticSerializer(source='stats')
    projects = ProjectPreviewSerializer(source='projects')
    campaign = CampaignSerializer(source='campaign')
    fundraisers = FundRaiserSerializer(source='fundraisers')
