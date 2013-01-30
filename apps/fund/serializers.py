from apps.bluebottle_drf2.serializers import SorlImageField, PolymorphicSerializer
from cowry_docdata.models import DocdataPaymentInfo
from cowry_ipay.models import Payment
from rest_framework import serializers
from rest_framework import relations
from rest_framework import fields
from .models import Donation, OrderItem
from cowry.models import Payment, PaymentAdapter, PaymentMethod, PaymentInfo


class DonationSerializer(serializers.ModelSerializer):
    project = relations.PrimaryKeyRelatedField(source='project')
    status = fields.Field()

    class Meta:
        model = Donation
        fields = ('id', 'project', 'amount', 'status')


class ObjectBasedSerializerOptions(serializers.SerializerOptions):

    def __init__(self, meta):
        super(ObjectBasedSerializerOptions, self).__init__(meta)
        self.child_models = getattr(meta, 'child_models', None)


class ObjectBasedSerializer(serializers.Serializer):
    """
    Redirect to another Serialzer based on the object type
    This is a copy-paste job from PolymorphicSerializer
    """
    # TODO: See if this code makes sense
    # TODO: Move to bluebottle_drf2

    _options_class = ObjectBasedSerializerOptions

    def __init__(self, instance=None, data=None, files=None, context=None, partial=False, **kwargs):
        super(ObjectBasedSerializer, self).__init__(instance, data, files, context, partial, **kwargs)
        self._child_models = {}
        for Model, Serializer in self.opts.child_models:
            self._child_models[Model] = Serializer()

    def field_to_native(self, obj, field_name):
        """
        Override so that we can use the child_model serializers.
        """
        obj = getattr(obj, self.source or field_name)


        return self._child_models[obj.__class__].to_native(obj)

    def convert_object(self, obj):
        """
        Override so that we can iterate through the child_model field items.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self._child_models[obj.__class__].fields.items():
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret

    class Meta:
        child_models = (
            (Donation, DonationSerializer),
            )


class OrderItemSerializer(serializers.ModelSerializer):
    amount = fields.Field(source='amount')
    type = fields.Field(source='type')
    item = ObjectBasedSerializer(source='content_object')

    # TODO: At conditional serializers for Donation or Voucher here on source='item'

    class Meta:
        model = OrderItem
        fields = ('amount', 'type', 'item')


# Payment Serializers

class PaymentAdapterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAdapter
        fields = ('id', 'title', 'slug', 'active')


class PaymentMethodSerializer(serializers.ModelSerializer):
    payment_adapter = PaymentAdapterSerializer()
    icon = SorlImageField('icon', '90x90')

    class Meta:
        model = PaymentMethod
        fields = ('id', 'title', 'slug', 'active', 'icon', 'payment_adapter')


class PaymentSerializer(serializers.ModelSerializer):
    amount = fields.Field(source='amount')
    created = fields.Field(source='created')
    status = fields.Field(source='status')
    payment_method = relations.PrimaryKeyRelatedField(source='payment_method')

    class Meta:
        model = Payment
        fields = ('id', 'created', 'status', 'amount', 'payment_method')


class PaymentInfoSerializerBase(serializers.ModelSerializer):
    id = serializers.Field(source='paymentinfo_ptr_id')
    amount = fields.Field(source='amount')
    status = fields.Field(source='status')
    payment_url = fields.Field(source='payment_url')

    class Meta:
        model = PaymentInfo
        fields = ('id', 'created', 'status', 'amount', 'payment_url')


class DocdataPaymentInfoSerializer(PaymentInfoSerializerBase):
    email = fields.WritableField(source='client_email')
    first_name = fields.WritableField(source='client_firstname')
    last_name = fields.WritableField(source='client_lastname')
    address = fields.WritableField(source='client_address')
    city = fields.WritableField(source='client_city')
    zip_code = fields.WritableField(source='client_zip')
    country = fields.WritableField(source='client_country')

    class Meta:
        model = DocdataPaymentInfo
        fields = PaymentInfoSerializerBase.Meta.fields + ('email', 'first_name', 'last_name', 'address', 'city',
                                                      'zip_code', 'country')


class PaymentInfoSerializer(PolymorphicSerializer):

    class Meta:
        child_models = (
            (DocdataPaymentInfo, DocdataPaymentInfoSerializer),
            )
