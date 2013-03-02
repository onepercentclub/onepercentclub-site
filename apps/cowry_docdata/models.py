from apps.cowry.models import Payment
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_countries import CountryField
from polymorphic.manager import PolymorphicManager
from polymorphic.polymorphic_model import PolymorphicModel


class DocDataPaymentOrder(Payment):
    # Payment information.
    payment_order_key = models.CharField(max_length=255, default='', blank=True)
    merchant_order_reference = models.CharField(max_length=100, default='', blank=True)

    # Order profile information.
    customer_id = models.IntegerField(default=0)  # Defaults to 0 for anonymous.
    email = models.EmailField(max_length=254, default='')
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    street = models.CharField(max_length=200, default='')
    postal_code = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=200, default='')
    country = CountryField()
    language = models.CharField(max_length=2, default='en')

    @property
    def latest_docdata_payment(self):
        if self.docdatapayment_set.all():
            return self.docdatapayment_set.order_by('-created').all()[0]
        return None


class DocDataPayment(PolymorphicModel):
    # Statuses from: Integration Manual Order API 1.0 - Document version 1.0, 08-12-2012 - Page 35

    statuses = ('NEW', 'STARTED', 'AUTHORIZED', 'PAID', 'CANCELLED', 'CHARGED-BACK', 'CONFIRMED_PAID',
                'CONFIRMED_CHARGEDBACK', 'CLOSED_SUCCESS', 'CLOSED_CANCELLED')

    status = models.CharField(_("status"), max_length=25, default='NEW')
    docdata_payment_order = models.ForeignKey(DocDataPaymentOrder)
    payment_id = models.PositiveIntegerField(_("payment id"), default=0)
    # This is the payment method id from DocData (e.g. IDEAL, MASTERCARD, etc)
    docdata_payment_method = models.CharField(max_length=20, default='', blank=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    objects = PolymorphicManager()


class DocDataWebMenu(DocDataPayment):
    payment_url = models.URLField(max_length=500, blank=True)


class DocDataWebDirectDirectDebit(DocDataPayment):
    bank_account_number = models.CharField(max_length=10, default='', blank=True)
    bank_account_name = models.CharField(max_length=100, default='', blank=True)
    bank_account_city = models.CharField(max_length=100, default='', blank=True)

