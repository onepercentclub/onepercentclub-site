from decimal import Decimal
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from apps.bluebottle_utils.fields import MoneyField


class Donation(models.Model):
    """
    Donation of an amount from a user to a project. A Donation can have a generic foreign key from OrderItem when
    it's used in the order process but it can also be used without this GFK when it's used to cash in a Voucher.
    """

    class DonationStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        in_progress = ChoiceItem('in_progress', label=_("In Progress"))
        paid = ChoiceItem('paid', label=_("Paid"))
        cancelled = ChoiceItem('cancelled', label=_("Cancelled"))

    amount = MoneyField(_("amount"))
    user = models.ForeignKey('auth.User', verbose_name=_("user"), null=True, blank=True)
    project = models.ForeignKey('projects.Project', verbose_name=_("project"))
    status = models.CharField(_("status"), max_length=20, choices=DonationStatuses.choices, default=DonationStatuses.new, db_index=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        return str(self.id) + ' : ' + self.project.title + ' : EUR ' + str(self.amount)


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).
    It can be in progress (eg a shopping cart) or processed and paid
    """

    class OrderStatuses(DjangoChoices):
        started = ChoiceItem('started', label=_("Started"))
        cancelled = ChoiceItem('cancelled', label=_("Cancelled"))
        checkout = ChoiceItem('checkout', label=_("Checkout"))
        new = ChoiceItem('new', label=_("New"))
        pending = ChoiceItem('pending', label=_("Pending"))
        failed = ChoiceItem('failed', label=_("Failed"))
        paid = ChoiceItem('paid', label=_("Paid"))

    user = models.ForeignKey('auth.User', verbose_name=_("user"), blank=True, null=True)
    status = models.CharField(_("status"),max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.started, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    recurring = models.BooleanField(default=False)
    payment = models.ForeignKey('cowry.Payment', null=True, blank=True)

    # Calculate total for this Order
    @property
    def amount(self):
        amount = Decimal('0')
        for item in self.orderitem_set.all():
            amount += item.amount
        return amount


class OrderItem(models.Model):
    """
    Typically this connects a Donation or a Voucher to an Order.
    """
    order = models.ForeignKey(Order)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Calculate properties for ease of use (e.g. in serializers).
    @property
    def amount(self):
        return self.content_object.amount

    @property
    def type(self):
        return self.content_object.__class__.__name__
