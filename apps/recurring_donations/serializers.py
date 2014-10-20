from apps.recurring_donations.models import MonthlyDonor, MonthlyDonorProject
from rest_framework import serializers


class MonthlyDonationProjectSerializer(serializers.ModelSerializer):

    project = serializers.SlugRelatedField(many=False, slug_field='slug')
    donation = serializers.PrimaryKeyRelatedField(source='donor')

    class Meta():
        model = MonthlyDonorProject
        fields = ('id', 'donation', 'project')


class MonthlyDonationSerializer(serializers.ModelSerializer):

    projects = MonthlyDonationProjectSerializer(many=True, read_only=True)

    class Meta():
        model = MonthlyDonor
        fields = ('id', 'amount', 'iban', 'bic', 'active', 'name', 'city', 'projects')
