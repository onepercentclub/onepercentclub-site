from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from polymorphic import PolymorphicModel


# # TODO change to django settings
# class PaymentMethod(models.Model):
#     title = models.CharField(max_length=100)
#     slug = models.CharField(max_length=100, unique=True)
#     payment_adapter = models.ForeignKey(PaymentAdapter)
#     costs_static = models.DecimalField(max_digits=12, decimal_places=4, default=0,
#                                        help_text=_("The set amount that each transaction costs"))
#     costs_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0,
#                                            help_text=_("The percentage that each transaction costs"))
#     icon = models.ImageField(_("icon"), max_length=255, blank=True, upload_to='payment_icons/',
#                              help_text=_("Icon for payment method"))
#     restricted = models.BooleanField(_("Is this payment method restricted to selected countries?"), default=False)
#     active = models.BooleanField()
#
#     def natural_key(self):
#         return self.slug
#
#     def __unicode__(self):
#         return self.title
#
#     class Meta:
#         # TODO: why are your specifying the db_tables?
#         db_table = "payments_paymentmethod"


# # TODO: I don't think this makes sense.
# class PaymentMethodCountry(models.Model):
#     method = models.ForeignKey(PaymentMethod)
#     country = CountryField()
#
#     class Meta:
#         db_table = "payments_paymentmethod_country"
from polymorphic.manager import PolymorphicManager


class Payment(PolymorphicModel):
    """
    TODO better comment: Payment. This holds the total amount due to pay.
    """

    class PaymentStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        in_progress = ChoiceItem('in_progress', label=_("In Progress"))
        paid = ChoiceItem('paid', label=_("Paid"))
        failed = ChoiceItem('failed', label=_("Failed"))
        cancelled = ChoiceItem('cancelled', label=_("Cancelled"))
        refunded = ChoiceItem('refunded', label=_("Refunded"))

    # The amount in the minor unit for the given currency (e.g. for EUR in cents).
    amount = models.PositiveIntegerField(_("amount"), default=0)
    currency = models.CharField(max_length=3, default='', blank=True)

    # The transaction cost that is taken by the payment service provider.
    fee = models.PositiveIntegerField(_("payment service fee"), default=0)

    # Payment method used
    payment_method = models.CharField(max_length=20, default='', blank=True)
    payment_submethod = models.CharField(max_length=20, default='', blank=True)

    status = models.CharField(_("status"), max_length=15, choices=PaymentStatuses.choices, default=PaymentStatuses.new, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    # Manager
    objects = PolymorphicManager()
