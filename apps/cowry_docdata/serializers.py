from apps.bluebottle_drf2.serializers import PolymorphicSerializer
from apps.cowry_docdata.models import DocDataWebMenu, DocDataWebDirectDirectDebit
from rest_framework import serializers
from .models import DocDataPayment


class DocDataOrderProfileSerializer(serializers.ModelSerializer):
    # # TODO Generate country list from docdata api and use ChoiceField.
    # country = serializers.CharField(required=True)
    serializers.Field(source='payment_ptr_id')

    class Meta:
        model = DocDataPayment
        fields = ('id', 'first_name', 'last_name', 'email', 'street', 'city', 'postal_code', 'country')


class DocDataPaymentMethodSerializer(PolymorphicSerializer):
    class Meta:
        child_models = (
            (DocDataWebMenu, DocDataWebMenuSerializer),
            (DocDataWebDirectDirectDebit, DocDataWebDirectDirectDebitSerializer),
        )


class DocDataPaymentMethodSerializerBase(PolymorphicSerializer):
    class Meta:
        fields = ('id', 'name', 'payment_submethod', 'payment_submethods')


class DocDataWebMenuSerializer(serializers.Serializer):
    class Meta:
        model = DocDataWebMenu
        fields = DocDataPaymentMethodSerializerBase.Meta.fields + ('payment_url',)


class DocDataWebDirectDirectDebitSerializer(serializers.Serializer):
    class Meta:
        model = DocDataWebDirectDirectDebit
        fields = DocDataPaymentMethodSerializerBase.Meta.fields + ('bank_account',)
