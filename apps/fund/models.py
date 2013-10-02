import logging
import random
from babel.numbers import format_currency
from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from djchoices import DjangoChoices, ChoiceItem
from bluebottle.accounts.models import BlueBottleUser
from apps.cowry.models import PaymentStatuses, Payment
from apps.cowry.signals import payment_status_changed
from .fields import DutchBankAccountField
from .mails import mail_new_voucher

logger = logging.getLogger(__name__)
random.seed()


class RecurringDirectDebitPayment(models.Model):
    """
    Holds the direct debit account and payment information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    active = models.BooleanField(default=False)
    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    # The amount in the minor unit for the given currency (e.g. for EUR in cents).
    amount = models.PositiveIntegerField(_("amount"), default=0)
    currency = models.CharField(max_length=3, default='')

    # Bank account.
    name = models.CharField(max_length=35)  # max_length from DocData
    city = models.CharField(max_length=35)  # max_length from DocData
    account = DutchBankAccountField()

    # IBAN fields required for DocData recurring donation processing.
    # These are not required because we will be filling these in manually (for now) and not presenting them to users.
    iban = IBANField(blank=True, default='')
    bic = SWIFTBICField(blank=True, default='')

    def __unicode__(self):
        if self.active:
            postfix = ' - active'
        else:
            postfix = ' - inactive'
        return str(self.user) + ' ' + str(self.amount) + postfix


@receiver(post_save, weak=False, sender=BlueBottleUser)
def cancel_recurring_payment_user_soft_delete(sender, instance, created, **kwargs):
    if created:
        return

    if hasattr(instance, 'recurringdirectdebitpayment') and instance.deleted:
        recurring_payment = instance.recurringdirectdebitpayment
        recurring_payment.active = False
        recurring_payment.save()


@receiver(post_delete, weak=False, sender=BlueBottleUser)
def cancel_recurring_payment_user_delete(sender, instance, **kwargs):

    if hasattr(instance, 'recurringdirectdebitpayment'):
        recurring_payment = instance.recurringdirectdebitpayment
        recurring_payment.delete()


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
    def payment_method(self):
        ctype = ContentType.objects.get_for_model(Donation)
        order_ids = OrderItem.objects.filter(content_type__pk=ctype.id,
                                             object_id=self.id).values_list('order_id', flat=True)
        payments = Payment.objects.filter(order_id__in=order_ids)
        for payment in payments:
            if getattr(payment, 'docdata_payments', False):
                docdata_payments = payment.docdata_payments.all()
                if docdata_payments:
                    return ", ".join([p.payment_method for p in docdata_payments])

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        language = translation.get_language().split('-')[0]
        if not language:
            language = 'en'
        return u'{0} : {1} : {2}'.format(str(self.id), self.project.title,
                                         format_currency(self.amount / 100.0, self.currency, locale=language))


class OrderStatuses(DjangoChoices):
    current = ChoiceItem('current', label=_("Current"))  # The single donation 'shopping cart' (editable).
    recurring = ChoiceItem('recurring', label=_("Recurring"))  # The recurring donation 'shopping cart' (editable).
    closed = ChoiceItem('closed', label=_("Closed"))     # Order with a paid, cancelled or failed payment (not editable).


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.current, db_index=True)
    recurring = models.BooleanField(default=False)
    order_number = models.CharField(_("Order Number"), max_length=30, db_index=True, unique=True, help_text="Used to reference the Order from external systems.")

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))

    @property
    def latest_payment(self):
        if self.payments.count() > 0:
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
    def total_euro(self):
        return "%01.2f" % (self.total / 100)

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
        description = ''
        if self.order_number:
            description += self.order_number + " - "

        description += "1%Club "
        if self.recurring:
            # TODO Use English / Dutch based on user primary_language.
            description += "MAANDELIJKSE DONATIE"
        elif not self.donations and self.vouchers:
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
        description += " - " + _("THANK YOU!")
        return description

    class Meta:
        ordering = ('-created',)

    # http://stackoverflow.com/questions/2076838
    def save(self, *args, **kwargs):
        if not self.order_number:
            loop_num = 0
            max_number = 1000000000  # 1 billion
            order_number = str(random.randint(0, max_number))
            while Order.objects.filter(order_number=order_number).exists():
                if loop_num > 1000:
                    raise ValueError(_("Couldn't generate a unique order number."))
                else:
                    order_number = str(random.randint(0, max_number))
                    loop_num += 1
            self.order_number = order_number
        super(Order, self).save(*args, **kwargs)


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
        if self.content_object:
            return self.content_object.amount
        return 0

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

    order = instance.order

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
    # Payment: -> cancelled; Order is 'current'
    #
    if new_status == PaymentStatuses.cancelled and order.status == OrderStatuses.current:

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.new
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> cancelled; Order is 'closed'
    #
    elif new_status == PaymentStatuses.cancelled and order.status == OrderStatuses.closed:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.failed
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> cancelled; Order is not 'closed' or 'current'
    #
    elif new_status == PaymentStatuses.cancelled:
        logger.error("PaymentStatuses.cancelled when Order {0} has status {1}.".format(order.id, order.status))

    #
    # Payment: -> pending
    #
    if new_status == PaymentStatuses.pending:
        if order.status != OrderStatuses.closed:
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
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.paid
            donation.save()

        # Vouchers.
        # TODO Implement vouchers.

    #
    # Payment: -> failed, refunded or chargedback
    #
    if new_status in [PaymentStatuses.failed, PaymentStatuses.refunded, PaymentStatuses.chargedback]:
        if order.status != OrderStatuses.closed:
            order.status = OrderStatuses.closed
            order.save()

        # Donations.
        for donation in order.donations:
            donation.status = DonationStatuses.failed
            donation.save()

        # Vouchers.
        for voucher in order.vouchers:
            voucher.status = VoucherStatuses.cancelled
            voucher.save()
