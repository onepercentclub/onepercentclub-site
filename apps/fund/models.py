import random
from apps.fund.mails import mail_new_voucher
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem


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

    @property
    def amount_euro(self):
        return self.amount / 100

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        return str(self.id) + ' : ' + self.project.title + ' : EUR ' + str(self.amount_euro)


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).

    """

    class OrderStatuses(DjangoChoices):
        """
            Current: Shopping cart.
            Monthly: Monthly order that can change until it's processed on the 1st day of the month.
            Closed: An order that has a payment that's in progress, paid, cancelled or failed.
        """
        # TODO: add validation rules for statuses.
        current = ChoiceItem('current', label=_("Current"))
        monthly = ChoiceItem('monthly', label=_("Monthly"))
        closed = ChoiceItem('closed', label=_("Closed"))

    user = models.ForeignKey('auth.User', verbose_name=_("user"), blank=True, null=True)
    status = models.CharField(_("status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.current, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    recurring = models.BooleanField(default=False)
    payment = models.ForeignKey('cowry.Payment', null=True, blank=True)

    # Calculate total for this Order
    @property
    def total(self):
        total = 0
        for item in self.orderitem_set.all():
            total += item.amount
        return total

    @property
    def donations(self):
        content_type = ContentType.objects.get_for_model(Donation)
        order_items = self.orderitem_set.filter(content_type=content_type)
        return Donation.objects.filter(id__in=order_items.values('object_id'))

    @property
    def vouchers(self):
        content_type = ContentType.objects.get_for_model(Voucher)
        order_items = self.orderitem_set.filter(content_type=content_type)
        return Voucher.objects.filter(id__in=order_items.values('object_id'))


class OrderItem(models.Model):
    """
    This connects a Donation or a Voucher to an Order. It's generic so that Donations don't have to know about Orders
    and so that we can add more Order types easily.
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

    status = models.CharField(_("status"), max_length=20, choices=VoucherStatuses.choices, default=VoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    sender = models.ForeignKey('auth.User', verbose_name=_("sender"), related_name="sender", null=True, blank=True)
    sender_email = models.EmailField(_("sender email"))
    sender_name = models.CharField(_("sender name"), blank=True, default="", max_length=100)

    receiver = models.ForeignKey('auth.User', verbose_name=_("receiver"), related_name="receiver", null=True, blank=True)
    receiver_email = models.EmailField(_("receiver email"))
    receiver_name = models.CharField(_("receiver name"), blank=True, default="", max_length=100)

    donations = models.ManyToManyField('Donation')

    @property
    def amount_euro(self):
        return self.amount / 100

    class Meta:
        verbose_name = _("voucher")
        verbose_name_plural = _("vouchers")


class CustomVoucherRequest(models.Model):

    class CustomVoucherTypes(DjangoChoices):
        card = ChoiceItem('card', label=_("Card"))
        digital = ChoiceItem('digital', label=_("Digital"))
        unknown = ChoiceItem('unknown', label=_("Unknown"))

    class CustomVoucherStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        in_progress = ChoiceItem('in progress', label=_("In progress"))
        finished = ChoiceItem('finished', label=_("Finished"))

    amount = models.IntegerField(_("Amount needed"))
    contact = models.ForeignKey('auth.User', verbose_name=_("Contact member"), null=True)
    contact_name = models.CharField(verbose_name=_("Contact email"), max_length=100, blank=True, default="")
    contact_email = models.EmailField(verbose_name=_("Contact email"), blank=True, default="")
    contact_phone = models.CharField(verbose_name=_("Contact phone"), max_length=100, blank=True, default="")
    organization = models.CharField(verbose_name=_("Organization"), max_length=200, blank=True, default="")
    message = models.TextField(_("message"), default="", max_length=500, blank=True)

    type = models.CharField(_("type"), max_length=20, choices=CustomVoucherTypes.choices, default=CustomVoucherTypes.unknown)
    status = models.CharField(_("status"), max_length=20, choices=CustomVoucherStatuses.choices, default=CustomVoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("created"))


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
    mail_new_voucher(voucher)


def process_donation_order_in_progress(donation):
    donation.status = Donation.DonationStatuses.in_progress
    donation.save()
