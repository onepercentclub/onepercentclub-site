from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from polymorphic import PolymorphicModel
from polymorphic.manager import PolymorphicManager


class Payment(PolymorphicModel):
    """
    Payment. This holds the total amount due to pay.
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
    payment_method_id = models.CharField(max_length=20, default='', blank=True)
    payment_submethod_id = models.CharField(max_length=20, default='', blank=True)

    status = models.CharField(_("status"), max_length=15, choices=PaymentStatuses.choices, default=PaymentStatuses.new, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    # Manager
    objects = PolymorphicManager()
