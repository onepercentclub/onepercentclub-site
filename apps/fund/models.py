import random
from django.conf import settings
from apps.cowry.models import PaymentStatuses, Payment
from apps.cowry.signals import payment_status_changed
from apps.fund.mails import mail_new_voucher
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import SWIFTBICField, IBANField
from djchoices import DjangoChoices, ChoiceItem


class RecurringDirectDebitPayment(models.Model):
    """
    Holds the direct debit account information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    active = models.BooleanField(default=False)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    # Bank account.
    name = models.CharField(max_length=35)  # max_length from DocData
    city = models.CharField(max_length=35)  # max_length from DocData
    iban = IBANField()
    bic = SWIFTBICField()


class DonationStatuses(DjangoChoices):
    new = ChoiceItem('new', label=_("New"))
    in_progress = ChoiceItem('in_progress', label=_("In progress"))
    pending = ChoiceItem('pending', label=_("Pending"))
    paid = ChoiceItem('paid', label=_("Paid"))
    failed = ChoiceItem('failed', label=_("Failed"))


class Donation(models.Model):
    """
    Donation of an amount from a user to a project. A Donation can have a generic foreign key from OrderItem when
    it's used in the order process but it can also be used without this GFK when it's used to cash in a Voucher.
    """
    class DonationTypes(DjangoChoices):
        one_off = ChoiceItem('one_off', label=_("One-off"))
        recurring = ChoiceItem('recurring', label=_("Recurring"))
        voucher = ChoiceItem('voucher', label=_("Voucher"))

    amount = models.PositiveIntegerField(_("Amount"))
    currency = models.CharField(_("currency"), max_length=3)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, blank=True)
    project = models.ForeignKey('projects.Project', verbose_name=_("Project"))

    status = models.CharField(_("Status"), max_length=20, choices=DonationStatuses.choices, default=DonationStatuses.new, db_index=True)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    donation_type = models.CharField(_("Type"), max_length=20, choices=DonationTypes.choices, default=DonationTypes.one_off, db_index=True)

    @property
    def amount_euro(self):
        return "%01.2f" % (self.amount / 100)

    @property
    def local_amount(self):
        return "%01.2f" % (self.amount / 100)

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        return str(self.id) + ' : ' + self.project.title + ' : EUR ' + str(self.amount_euro)


class OrderStatuses(DjangoChoices):
    current = ChoiceItem('current', label=_("Current"))  # The single donation 'shopping cart' (editable).
    recurring = ChoiceItem('recurring', label=_("Recurring"))  # The recurring donation 'shopping cart' (editable).
    closed = ChoiceItem('closed', label=_("Closed"))     # Order with a paid, cancelled or failed payment (not editable).


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), blank=True, null=True)
    status = models.CharField(_("status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.current, db_index=True)

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    recurring = models.BooleanField(default=False)

    # Note this is a ManyToMany so that there is no Order FK on the Payment. Payments don't have multiple Orders.
    payments = models.ManyToManyField('cowry.Payment', related_name='orders')

    @property
    def latest_payment(self):
        if self.payments.all():
            return self.payments.order_by('-created').all()[0]
        return None

    @property
    def total(self):
        """ Calculated total for this Order. """
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

    def __unicode__(self):
        description = "1%CLUB "
        if not self.donations and self.vouchers:
            if len(self.donations) > 1:
                description += _("GIFTCARDS")
            else:
                description += _("GIFTCARD")
            description += str(self.id)
        elif self.donations and not self.vouchers:
            if len(self.donations) > 1:
                description += _("DONATIONS")
            else:
                description += _("DONATION")
        else:
            description += _("DONATIONS & GIFTCARDS")
        description += " " + str(self.id) + " " + "- " + _("THANK YOU!")
        return description


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


class VoucherStatuses(DjangoChoices):
    new = ChoiceItem('new', label=_("New"))
    paid = ChoiceItem('paid', label=_("Paid"))
    cancelled = ChoiceItem('cancelled', label=_("Cancelled"))
    cashed = ChoiceItem('cashed', label=_("Cashed"))
    cashed_by_proxy = ChoiceItem('cashed_by_proxy', label=_("Cashed by us"))


class Voucher(models.Model):

    class VoucherLanguages(DjangoChoices):
        en = ChoiceItem('en', label=_("English"))
        nl = ChoiceItem('nl', label=_("Dutch"))

    amount = models.PositiveIntegerField(_("Amount"))
    currency = models.CharField(_("Currency"), blank=True, max_length=3)

    language = models.CharField(_("Language"), max_length=2, choices=VoucherLanguages.choices, default=VoucherLanguages.en)
    message = models.TextField(_("Message"), blank=True, default="", max_length=500)
    code = models.CharField(_("Code"), blank=True, default="", max_length=100)

    status = models.CharField(_("Status"), max_length=20, choices=VoucherStatuses.choices, default=VoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Sender"), related_name="sender", null=True, blank=True)
    sender_email = models.EmailField(_("Sender email"))
    sender_name = models.CharField(_("Sender name"), blank=True, default="", max_length=100)

    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Receiver"), related_name="receiver", null=True, blank=True)
    receiver_email = models.EmailField(_("Receiver email"))
    receiver_name = models.CharField(_("Receiver name"), blank=True, default="", max_length=100)

    donations = models.ManyToManyField('Donation')

    @property
    def amount_euro(self):
        return self.amount / 100

    class Meta:
        # Note: This can go back to 'Voucher' when we figure out a proper way to do EN -> EN translations for branding.
        verbose_name = _("Gift Card")
        verbose_name_plural = _("Gift Cards")


class CustomVoucherRequest(models.Model):

    class CustomVoucherTypes(DjangoChoices):
        card = ChoiceItem('card', label=_("Card"))
        digital = ChoiceItem('digital', label=_("Digital"))
        unknown = ChoiceItem('unknown', label=_("Unknown"))

    class CustomVoucherStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        in_progress = ChoiceItem('in progress', label=_("In progress"))
        finished = ChoiceItem('finished', label=_("Finished"))

    value = models.CharField(verbose_name=_("Value"), max_length=100, blank=True, default="")
    number = models.PositiveIntegerField(_("Number"))
    contact = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Contact member"), null=True)
    contact_name = models.CharField(verbose_name=_("Contact email"), max_length=100, blank=True, default="")
    contact_email = models.EmailField(verbose_name=_("Contact email"), blank=True, default="")
    contact_phone = models.CharField(verbose_name=_("Contact phone"), max_length=100, blank=True, default="")
    organization = models.CharField(verbose_name=_("Organisation"), max_length=200, blank=True, default="")
    message = models.TextField(_("message"), default="", max_length=500, blank=True)

    type = models.CharField(_("type"), max_length=20, choices=CustomVoucherTypes.choices, default=CustomVoucherTypes.unknown)
    status = models.CharField(_("status"), max_length=20, choices=CustomVoucherStatuses.choices, default=CustomVoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("created"))


def process_voucher_order_in_progress(voucher):
    def generate_voucher_code():
        # Upper case letters without D, O, L and I; Numbers without 0 and 1.
        char_set = 'ABCEFGHJKMNPQRSTUVWXYZ23456789'
        return ''.join(random.choice(char_set) for i in range(8))

    code = generate_voucher_code()
    while Voucher.objects.filter(code=code).exists():
        code = generate_voucher_code()

    voucher.code = code
    voucher.status = VoucherStatuses.paid
    voucher.save()
    mail_new_voucher(voucher)


@receiver(payment_status_changed, sender=Payment)
def process_payment_status_changed(sender, instance, old_status, new_status, **kwargs):
    # Payment statuses: new
    #                   in_progress
    #                   pending
    #                   paid
    #                   failed
    #                   cancelled
    #                   refunded
    #                   unknown

    # Ignore status changes on payments that don't have an Order. This is needed to run the Cowry unit tests.
    # We could remove this check if we changed the unit tests to only test the full Order and Payment system.
    if instance.orders.all():
        order = instance.orders.all()[0]
    else:
        return

    #
    # Payment: new -> in_progress
    #
    if old_status == PaymentStatuses.new and new_status == PaymentStatuses.in_progress:
        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.in_progress
            donation.save()

        # Vouchers.
        for voucher in order.vouchers:
            process_voucher_order_in_progress(voucher)

    #
    # Payment: in_progress -> cancelled
    #
    if old_status == PaymentStatuses.in_progress and new_status == PaymentStatuses.cancelled:
        # TODO verify that order status is still current, change and print warning if not??
        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.new
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> pending
    #
    if new_status == PaymentStatuses.pending:
        order.status = OrderStatuses.closed
        order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.pending
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> paid
    #
    if new_status == PaymentStatuses.paid:
        order.status = OrderStatuses.closed
        order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.paid
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> failed or refunded
    #
    if new_status in [PaymentStatuses.failed, PaymentStatuses.refunded]:
        # FIXME Since we're using the 'current' alias instead of PKs there could be two order with current.
        order.status = OrderStatuses.current
        order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.failed
            donation.save()

        # Vouchers.
        for voucher in order.vouchers:
            voucher.status = VoucherStatuses.cancelled
            voucher.save()
