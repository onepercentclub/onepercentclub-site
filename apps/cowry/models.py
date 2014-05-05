from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from polymorphic import PolymorphicModel


class PaymentStatuses(DjangoChoices):
    new = ChoiceItem('new', label=_("New"))
    in_progress = ChoiceItem('in_progress', label=_("In Progress"))
    pending = ChoiceItem('pending', label=_("Pending"))
    paid = ChoiceItem('paid', label=_("Paid"))
    failed = ChoiceItem('failed', label=_("Failed"))
    cancelled = ChoiceItem('cancelled', label=_("Cancelled"))
    chargedback = ChoiceItem('chargedback', label=_("Chargedback"))
    refunded = ChoiceItem('refunded', label=_("Refunded"))
    unknown = ChoiceItem('unknown', label=_("Unknown"))  # Payments with this status have not been mapped.


class Payment(PolymorphicModel):
    """
    Payment. This holds the total amount due to pay.
    """
    # The amount in the minor unit for the given currency (e.g. for EUR in cents).
    amount = models.PositiveIntegerField(_("amount"), default=0)
    currency = models.CharField(max_length=3, default='')

    # The transaction cost that is taken by the payment service provider.
    fee = models.PositiveIntegerField(_("payment service fee"), default=0)

    # Payment method used
    payment_method_id = models.CharField(max_length=20, default='', blank=True)
    payment_submethod_id = models.CharField(max_length=20, default='', blank=True)

    status = models.CharField(_("status"), max_length=15, choices=PaymentStatuses.choices, default=PaymentStatuses.new, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    order = models.ForeignKey('fund.Order', related_name='payments')


class PaymentLogLevels(DjangoChoices):
    info = ChoiceItem('info', label=_("INFO"))
    warn = ChoiceItem('warn', label=_("WARN"))
    error = ChoiceItem('error', label=_("ERROR"))


# TODO: Add fields for: source file, source line number, source version, IP
class PaymentLogEntry(models.Model):
    message = models.CharField(max_length=400)
    level = models.CharField(max_length=15, choices=PaymentLogLevels.choices)
    timestamp = CreationDateTimeField()
    # TODO: Enable when not abstract.
    # payment = models.ForeignKey(Payment, related_name='log_entries')

    class Meta:
        # TODO: This shouldn't be abstract but for various reasons it's harder to deal with in the admin.
        abstract = True
        ordering = ('-timestamp',)
        verbose_name = _("Payment Log")
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0} {1}'.format(self.get_level_display(), Truncator(self.message).words(6))

    def log_entry(self):
        return '[{0}]  {1: <5}  {2 <5}  {3}'.format(self.timestamp.strftime("%d/%b/%Y %H:%M:%S"),
                                                    self.get_type_display(), self.get_level_display(), self.message)
