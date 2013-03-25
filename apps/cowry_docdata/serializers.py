from apps.bluebottle_drf2.serializers import PolymorphicSerializer
from rest_framework import serializers
from .models import DocDataPaymentOrder, DocDataWebMenu, DocDataWebDirectDirectDebit


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # TODO Generate country list from docdata api and use ChoiceField.
    country = serializers.CharField(required=True)

    class Meta:
        model = DocDataPaymentOrder
        fields = ('id', 'first_name', 'last_name', 'email', 'street', 'city', 'postal_code', 'country')


class DocDataWebMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocDataWebMenu
        fields = ('id', 'payment_url',)


class DocDataWebDirectDirectDebitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocDataWebDirectDirectDebit
        fields = ('id', 'bank_account_number', 'bank_account_name', 'bank_account_city')


class DocDataPaymentMethodSerializer(PolymorphicSerializer):
    class Meta:
        child_models = (
            (DocDataWebMenu, DocDataWebMenuSerializer),
            (DocDataWebDirectDirectDebit, DocDataWebDirectDirectDebitSerializer),
        )
