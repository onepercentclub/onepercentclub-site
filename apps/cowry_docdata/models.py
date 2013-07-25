from apps.cowry.models import Payment
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_countries import CountryField
from polymorphic import PolymorphicModel


class DocDataPaymentOrder(Payment):
    # Payment information.
    payment_order_id = models.CharField(max_length=200, default='', blank=True)
    merchant_order_reference = models.CharField(max_length=100, default='', blank=True)

    # Order profile information.
    customer_id = models.IntegerField(default=0)  # Defaults to 0 for anonymous.
    email = models.EmailField(max_length=254, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    address = models.CharField(max_length=200, default='')
    postal_code = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=200, default='')
    # TODO We should use the DocData Country list here.
    country = CountryField()
    language = models.CharField(max_length=2, default='en')

    @property
    def latest_docdata_payment(self):
        if self.docdata_payments.count() != 0:
            return self.docdata_payments.order_by('-created').all()[0]
        return None


class DocDataPayment(PolymorphicModel):
    """
    The base model for a docdata payment. The model can be used for a web menu payment.
    """
    # Statuses from: Integration Manual Order API 1.0 - Document version 1.0, 08-12-2012 - Page 35
    # Note; We're not using DjangoChoices here so that we can write unknown statuses if they are presented by DocData.
    statuses = ('NEW', 'STARTED', 'AUTHORIZED', 'AUTHORIZATION_REQUESTED', 'PAID', 'CANCELLED', 'CHARGED-BACK',
                'CONFIRMED_PAID', 'CONFIRMED_CHARGEDBACK', 'CLOSED_SUCCESS', 'CLOSED_CANCELLED')

    status = models.CharField(_("status"), max_length=30, default='NEW')
    docdata_payment_order = models.ForeignKey(DocDataPaymentOrder, related_name='docdata_payments')
    payment_id = models.CharField(_("payment id"), max_length=100, default='', blank=True)
    # This is the payment method id from DocData (e.g. IDEAL, MASTERCARD, etc)
    docdata_payment_method = models.CharField(max_length=20, default='', blank=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))


class DocDataWebDirectDirectDebit(DocDataPayment):
    bank_account_number = models.CharField(max_length=10, default='', blank=True)
    bank_account_name = models.CharField(max_length=100, default='', blank=True)
    bank_account_city = models.CharField(max_length=100, default='', blank=True)

