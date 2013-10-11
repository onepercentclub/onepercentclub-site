import random
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from .mails import mail_new_voucher


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
    currency = models.CharField(_("Currency"), max_length=3, default='EUR')

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

    order = models.ForeignKey('fund.Order', verbose_name=_("Order"), related_name='vouchers', null=True)

    class Meta:
        # Note: This can go back to 'Voucher' when we figure out a proper way to do EN -> EN translations for branding.
        verbose_name = _("Gift Card")
        verbose_name_plural = _("Gift Cards")

    def __unicode__(self):
        code = "NEw"
        if self.code:
            code = self.code
        return code


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
        # Upper case letters without D, O, L and I; numbers without 0 and 1.
        char_set = 'ABCEFGHJKMNPQRSTUVWXYZ23456789'
        return ''.join(random.choice(char_set) for i in range(8))

    code = generate_voucher_code()
    while Voucher.objects.filter(code=code).exists():
        code = generate_voucher_code()

    voucher.code = code
    voucher.status = VoucherStatuses.paid
    voucher.save()
    mail_new_voucher(voucher)
