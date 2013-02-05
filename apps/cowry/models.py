from django.db import models
from django.utils.translation import ugettext as _
from django_countries import CountryField
from django_extensions.db.fields import  ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from polymorphic import PolymorphicModel


class PaymentAdapterManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class PaymentAdapter(models.Model):

    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    api_url = models.URLField()
    api_test_url = models.URLField()
    active = models.BooleanField()
    objects = PaymentAdapterManager()

    def natural_key(self):
        return self.slug

    def __unicode__(self):
        return self.title

    class Meta:
        db_table = "payments_adapters"


class PaymentMethod(models.Model):

    title = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    payment_adapter = models.ForeignKey(PaymentAdapter)
    costs_static = models.DecimalField(max_digits=12, decimal_places=4, default=0, help_text=_("The set amount that each transaction costs"))
    costs_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0, help_text=_("The percentage that each transaction costs"))
    icon = models.ImageField(_("icon"), max_length=255, blank=True, upload_to='payment_icons/', help_text=_("Icon for payment method"))
    restricted = models.BooleanField(_("Is this payment method restricted to selected countries?"), default=False)
    active = models.BooleanField()

    def natural_key(self):
        return self.slug

    def __unicode__(self):
        return self.title

    class Meta:
        # TODO: why are your specifying the db_tables?
        db_table = "payments_paymentmethod"


# TODO: I don't think this makes sense.
class PaymentMethodCountry(models.Model):
    method = models.ForeignKey(PaymentMethod)
    country = CountryField()

    class Meta:
        db_table = "payments_paymentmethod_country"


class PaymentInfo(PolymorphicModel):
    payment_url = models.URLField(blank=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))
    amount = models.DecimalField(_("amount"), max_digits=9, decimal_places=2)

    class Meta:
        db_table = "payments_paymentinfo"


class Payment(models.Model):
    """
    Payment. This holds he total amount due to pay
    and reference to a Payment Process.
    All payment specific client data is stored in Payment Process.
    """

    class PaymentStatuses(DjangoChoices):
        checkout = ChoiceItem('checkout', label=_("Checkout"))
        new = ChoiceItem('new', label=_("New"))
        started = ChoiceItem('started', label=_("Started"))
        paid = ChoiceItem('paid', label=_("Paid"))

    amount = models.DecimalField(_("amount"), max_digits=9, decimal_places=2)

    # Amount taken by PSP
    ps_fee = models.DecimalField(_("ps fee"), max_digits=9, decimal_places=2, default=0)

    # Payment method used
    payment_method = models.ForeignKey(PaymentMethod, null=True)
    payment_info = models.ForeignKey(PaymentInfo, null=True, blank=True)

    # Note: having an index here allows for efficient filtering by status.
    status = models.CharField(_("status"),max_length=20, choices=PaymentStatuses.choices, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        db_table = "payments_payment"
