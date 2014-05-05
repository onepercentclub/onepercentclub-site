from apps.cowry.models import Payment, PaymentLogEntry
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_countries import CountryField
from django_iban.fields import IBANField, SWIFTBICField
from polymorphic import PolymorphicModel


# Maps a payment method to a consistent, human readable name.
payment_method_mapping = {
    'IDEAL': 'iDeal',
    'MASTERCARD': 'Mastercard',
    'VISA': 'Visa',
    'DIRECT_DEBIT': 'Direct debit',
    'SEPA_DIRECT_DEBIT': 'Direct debit',
    'ideal-rabobank-1procentclub_nl': 'iDeal',
    'paypal-1procentclub_nl': 'PayPal',
    'omnipay-ems-visa-1procentclub_nl': 'Visa',
    'banksys-mrcash-1procentclub_nl': 'Other',
    'ing-ideal-1procentclub_nl': 'iDeal',
    'SOFORT_UEBERWEISUNG-SofortUeberweisung-1procentclub_nl': 'Other',
    'ideal-ing-1procentclub_nl': 'iDeal',
    'system-banktransfer-nl': 'Bank transfer',
    'directdebitnc-online-nl': 'Direct debit',
    'directdebitnc2-online-nl': 'Direct debit',
    'omnipay-ems-maestro-1procentclub_nl': 'Other',
    '': 'Unknown',
    'omnipay-ems-mc-1procentclub_nl': 'Mastercard',
    'EBANKING': 'Other',
    'SOFORT_UEBERWEISUNG': 'Other',
    'MAESTRO': 'Other',
    'MISTERCASH': 'Other',
    'Gift Card': 'Gift Card'
}


class DocDataPaymentOrder(Payment):
    # Payment information.
    payment_order_id = models.CharField(max_length=200, default='', blank=True)
    merchant_order_reference = models.CharField(max_length=100, default='', blank=True)

    # Order profile information.
    customer_id = models.PositiveIntegerField(default=0)  # Defaults to 0 for anonymous.
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
        if self.docdata_payments.count() > 0:
            return self.docdata_payments.order_by('-created').all()[0]
        return None

    def __unicode__(self):
        if self.payment_order_id:
            return self.payment_order_id
        else:
            return 'NEW'

    class Meta:
        ordering = ('-created', '-updated')
        verbose_name = _("DocData Payment")
        verbose_name_plural = _("DocData Payments")


class DocDataPayment(PolymorphicModel):
    """
    The base model for a docdata payment. The model can be used for a web menu payment.
    """
    # Note: We're not using DjangoChoices here so that we can write unknown statuses if they are presented by DocData.
    status = models.CharField(_("status"), max_length=30, default='NEW')
    docdata_payment_order = models.ForeignKey(DocDataPaymentOrder, related_name='docdata_payments')
    payment_id = models.CharField(_("payment id"), max_length=100, default='', blank=True)
    # This is the payment method id from DocData (e.g. IDEAL, MASTERCARD, etc)
    payment_method = models.CharField(max_length=60, default='', blank=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    def __unicode__(self):
        return self.payment_id

    class Meta:
        ordering = ('-created', '-updated')


class DocDataWebDirectDirectDebit(DocDataPayment):
    account_name = models.CharField(max_length=35)  # max_length from DocData
    account_city = models.CharField(max_length=35)  # max_length from DocData
    iban = IBANField()
    bic = SWIFTBICField()


# TODO: Remove and use only PaymentLogEntry.
class DocDataPaymentLogEntry(PaymentLogEntry):
    docdata_payment_order = models.ForeignKey(DocDataPaymentOrder, related_name='log_entries')

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _("DocData Payment Log")
        verbose_name_plural = verbose_name
