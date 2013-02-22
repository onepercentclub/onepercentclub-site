from decimal import Decimal
import random
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

    amount = models.PositiveIntegerField(_("amount"))
    currency = models.CharField(_("currency"), blank=True, max_length=3)

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
    status = models.CharField(_("status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.started, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    recurring = models.BooleanField(default=False)
    payment = models.ForeignKey('cowry.Payment', null=True, blank=True)

    # Calculate total for this Order
    @property
    def amount(self):
        amount = 0
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


class Voucher(models.Model):

    class VoucherStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        paid = ChoiceItem('paid', label=_("Paid"))
        cashed = ChoiceItem('cashed', label=_("Cashed"))
        cashed_by_proxy = ChoiceItem('cashed_by_proxy', label=_("Cashed by us"))

    class VoucherLanguages(DjangoChoices):
        en = ChoiceItem('en', label=_("English"))
        nl = ChoiceItem('nl', label=_("Dutch"))

    amount = models.PositiveIntegerField(_("amount"))
    currency = models.CharField(_("currency"), blank=True, max_length=3)

    language = models.CharField(_("language"), max_length=2, choices=VoucherLanguages.choices, default=VoucherLanguages.en)
    message = models.TextField(_("message"), blank=True, default="", max_length=500)
    code = models.CharField(_("code"), blank=True, default="", max_length=100)

    sender = models.ForeignKey('auth.User', verbose_name=_("sender"), related_name="sender", null=True, blank=True)
    sender_email = models.EmailField(_("sender email"))
    sender_name = models.CharField(_("sender name"), blank=True, default="", max_length=100)

    receiver = models.ForeignKey('auth.User', verbose_name=_("receiver"), related_name="receiver", null=True, blank=True)
    receiver_email = models.EmailField(_("receiver email"))
    receiver_name = models.CharField(_("receiver name"), blank=True, default="", max_length=100)

    status = models.CharField(_("status"), max_length=20, choices=VoucherStatuses.choices, default=VoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))


def _generate_voucher_code():
    # Lower case letters without d, o and i. Numbers without 0 and 1.
    char_set = 'abcefghjklmnpqrstuvwxyz23456789'
    return ''.join(random.choice(char_set) for i in range(8))

def process_voucher_order_in_progress(voucher):
    code = _generate_voucher_code()
    while Voucher.objects.filter(code=code).exists():
        code = _generate_voucher_code()

    voucher.code = code
    voucher.status = Voucher.VoucherStatuses.paid
    voucher.save()

    # TODO Uncomment this when Loek's code is merged in.
    # mail_new_voucher(voucher)

def process_donation_order_in_progress(donation):
    donation.status = Donation.DonationStatuses.in_progress
    donation.save()
