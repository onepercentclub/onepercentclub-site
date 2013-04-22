import random
from apps.cowry.models import PaymentStatuses, Payment
from apps.cowry.signals import payment_status_changed
from apps.fund.mails import mail_new_voucher
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
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
        in_progress = ChoiceItem('in_progress', label=_("In progress"))
        paid = ChoiceItem('paid', label=_("Paid"))
        cancelled = ChoiceItem('cancelled', label=_("Cancelled"))

    class DonationTypes(DjangoChoices):
        one_off = ChoiceItem('one_off', label=_("One-off"))
        monthly = ChoiceItem('monthly', label=_("Monthly"))
        voucher = ChoiceItem('voucher', label=_("Voucher"))

    amount = models.PositiveIntegerField(_("Amount"))
    currency = models.CharField(_("currency"), blank=True, max_length=3)

    user = models.ForeignKey('auth.User', verbose_name=_("User"), null=True, blank=True)
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
    """
        Current: Shopping cart.
        Monthly: Monthly order that can change until it's processed on the 1st day of the month.
        Checkout: User is directed to payment provider
        Closed: An order that has a payment that's in progress, paid, cancelled or failed.
    """
    # TODO: add validation rules for statuses.
    current = ChoiceItem('current', label=_("Current"))
    monthly = ChoiceItem('monthly', label=_("Monthly"))
    checkout = ChoiceItem('checkout', label=_("Checkout"))
    closed = ChoiceItem('closed', label=_("Closed"))


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).
    """
    user = models.ForeignKey('auth.User', verbose_name=_("user"), blank=True, null=True)
    status = models.CharField(_("status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.current, db_index=True)

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    recurring = models.BooleanField(default=False)
    payments = models.ManyToManyField('cowry.Payment', related_name='orders')

    @property
    def payment(self):
        if self.payments.all():
            return self.payments.order_by('-created').all()[0]
        return None

    # When a user finalized the paymen flow this property is ticked. So it acts as a command.
    finalized = models.BooleanField(_("Finalized"), default=False)

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

    amount = models.PositiveIntegerField(_("Amount"))
    currency = models.CharField(_("Currency"), blank=True, max_length=3)

    language = models.CharField(_("Language"), max_length=2, choices=VoucherLanguages.choices, default=VoucherLanguages.en)
    message = models.TextField(_("Message"), blank=True, default="", max_length=500)
    code = models.CharField(_("Code"), blank=True, default="", max_length=100)

    status = models.CharField(_("Status"), max_length=20, choices=VoucherStatuses.choices, default=VoucherStatuses.new, db_index=True)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    sender = models.ForeignKey('auth.User', verbose_name=_("Sender"), related_name="sender", null=True, blank=True)
    sender_email = models.EmailField(_("Sender email"))
    sender_name = models.CharField(_("Sender name"), blank=True, default="", max_length=100)

    receiver = models.ForeignKey('auth.User', verbose_name=_("Receiver"), related_name="receiver", null=True, blank=True)
    receiver_email = models.EmailField(_("Receiver email"))
    receiver_name = models.CharField(_("Receiver name"), blank=True, default="", max_length=100)

    donations = models.ManyToManyField('Donation')

    @property
    def amount_euro(self):
        return self.amount / 100

    class Meta:
        # Note: This can go back to 'Voucher' when we figure out a proper way to do EN -> EN translations for branding.
        verbose_name = _("GiftCard")
        verbose_name_plural = _("GiftCards")


class CustomVoucherRequest(models.Model):

    class CustomVoucherTypes(DjangoChoices):
        card = ChoiceItem('card', label=_("Card"))
        digital = ChoiceItem('digital', label=_("Digital"))
        unknown = ChoiceItem('unknown', label=_("Unknown"))

    class CustomVoucherStatuses(DjangoChoices):
        new = ChoiceItem('new', label=_("New"))
        in_progress = ChoiceItem('in progress', label=_("In progress"))
        finished = ChoiceItem('finished', label=_("Finished"))

    number = models.PositiveIntegerField(_("Number"))
    contact = models.ForeignKey('auth.User', verbose_name=_("Contact member"), null=True)
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
        # Lower case letters without d, o, l and i. Numbers without 0 and 1.
        char_set = 'abcefghjkmnpqrstuvwxyz23456789'
        return ''.join(random.choice(char_set) for i in range(8))

    code = generate_voucher_code()
    while Voucher.objects.filter(code=code).exists():
        code = generate_voucher_code()

    voucher.code = code
    voucher.status = Voucher.VoucherStatuses.paid
    voucher.save()
    mail_new_voucher(voucher)


def set_donation_in_progress(donation):
    donation.status = Donation.DonationStatuses.in_progress
    donation.save()
    project = donation.project
    # Progress project to act phase if it's fully funded
    if project.money_needed <= 0:
        project.phase = 'act'
        project.save()


def set_donation_cancelled(donation):
    donation.status = Donation.DonationStatuses.cancelled
    donation.save()
    project = donation.project
    # Change project back to fund phase if it's not fully funded
    if project.money_needed > 0:
        project.phase = 'fund'
        project.save()


def set_donation_paid(donation):
    donation.status = Donation.DonationStatuses.paid
    donation.save()
    project = donation.project
    # Change project act phase if it's fully funded and still in fund phase
    if project.money_needed > 0 and project.phase == 'fund':
        project.phase = 'act'
        project.save()


def close_order_after_payment(order):
    # FIXME: make sure we have a payment
    # FIXME: make sure payment didn't update order/donation prior.
    # FIXME: Deal with vouchers

    for donation in order.donations:
        set_donation_in_progress(donation)

    order.status = OrderStatuses.closed
    order.save()


@receiver(payment_status_changed, sender=Payment)
def process_payment_status_changed(sender, instance, old_status, new_status, **kwargs):
    # Payment statuses: new
    #                   in_progress
    #                   paid
    #                   failed
    #                   cancelled
    #                   refunded

    # Ignore status changes on payments that don't have an Order. This is needed to run the Cowry unit tests.
    # We could remove this check if we changed the unit tests to only test the full Order and Payment system.
    if instance.orders.all():
        order = instance.orders.all()[0]
    else:
        return

    # Payment: new -> in_progress
    if old_status == PaymentStatuses.new and new_status == PaymentStatuses.in_progress:
        order.status = OrderStatuses.checkout
        order.save()
        for donation in order.donations:
            set_donation_in_progress(donation)

    # Payment: -> paid
    if new_status == PaymentStatuses.paid:
        order.status = OrderStatuses.closed
        order.save()
        for donation in order.donations:
            set_donation_paid(donation)

    # Payment: -> failed or cancelled or refunded
    if new_status in [PaymentStatuses.failed, PaymentStatuses.cancelled, PaymentStatuses.refunded]:
        order.status = OrderStatuses.checkout
        order.save()
        for donation in order.donations:
            set_donation_cancelled(donation)
