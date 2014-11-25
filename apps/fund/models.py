import logging
import random

from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import translation
from django.utils import timezone
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from djchoices import DjangoChoices, ChoiceItem

from babel.numbers import format_currency
from registration.signals import user_activated


from apps.cowry_docdata.models import DocDataPaymentOrder
from apps.vouchers.models import VoucherStatuses
from .fields import DutchBankAccountField


logger = logging.getLogger(__name__)
random.seed()


class DonationStatuses(DjangoChoices):
    new = ChoiceItem('new', label=_("New"))
    in_progress = ChoiceItem('in_progress', label=_("In progress"))
    pending = ChoiceItem('pending', label=_("Pending"))
    paid = ChoiceItem('paid', label=_("Paid"))
    failed = ChoiceItem('failed', label=_("Failed"))


class ValidDonationsManager(models.Manager):
    def get_queryset(self):
        queryset = super(ValidDonationsManager, self).get_queryset()
        return queryset.filter(status__in=(DonationStatuses.pending, DonationStatuses.paid))


class Donation(models.Model):
    """
    Donation of an amount from a user to a project.
    """
    class DonationTypes(DjangoChoices):
        one_off = ChoiceItem('one_off', label=_("One-off"))
        recurring = ChoiceItem('recurring', label=_("Recurring"))
        voucher = ChoiceItem('voucher', label=_("Voucher"))

    amount = models.PositiveIntegerField(_("amount (in cents)"))
    currency = models.CharField(_("currency"), max_length=3, default='EUR')

    # User is just a cache of the order user.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), null=True, blank=True)
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL, verbose_name=_("Project"), related_name='old_donations')
    fundraiser = models.ForeignKey('fundraisers.FundRaiser', verbose_name=_("fund raiser"), related_name='old_donations', null=True, blank=True)

    status = models.CharField(_("Status"), max_length=20, choices=DonationStatuses.choices, default=DonationStatuses.new, db_index=True)

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))
    # The timestamp the donation changed to pending or paid. This is auto-set in the save() method.
    ready = models.DateTimeField(_("Ready"), blank=True, editable=False, null=True)

    donation_type = models.CharField(_("Type"), max_length=20, choices=DonationTypes.choices, default=DonationTypes.one_off, db_index=True)

    order = models.ForeignKey('Order', verbose_name=_("Order"), related_name='donations', null=True, blank=True)
    voucher = models.ForeignKey('vouchers.Voucher', verbose_name=_("Gift card"), null=True, blank=True)

    objects = models.Manager()
    valid_donations = ValidDonationsManager()

    @property
    def payment_method(self):
        """ The DocData payment method. """
        if self.donation_type == self.DonationTypes.voucher:
            return "Gift Card"
        latest_payment = self.order.latest_payment
        if latest_payment:
            if getattr(latest_payment, 'docdata_payments', False):
                latest_docdata_payment = latest_payment.latest_docdata_payment
                if latest_docdata_payment:
                    return latest_docdata_payment.payment_method

        return ''

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        language = translation.get_language().split('-')[0]
        if not language:
            language = 'en'
        return u'{0} - {1} - {2}'.format(str(self.id), self.project.title,
                                         format_currency(self.amount / 100.0, self.currency, locale=language))

    def save(self, *args, **kwargs):
        # Automatically set the user and donation_type based on the order. This is required so that donations always
        # have the correct user and donation_type regardless of how they are created. User is just a cache of the order
        # user.
        if not self.order and not self.voucher:
            raise Exception("Either Order or Voucher should be set.")

        if self.order:
            if self.order.user != self.user:
                self.user = self.order.user
            if self.order.recurring and self.donation_type != self.DonationTypes.recurring:
                self.donation_type = self.DonationTypes.recurring
            elif not self.order.recurring and self.donation_type != self.DonationTypes.one_off:
                self.donation_type = self.DonationTypes.one_off

        if self.voucher:
            self.donation_type = self.DonationTypes.voucher
            if self.voucher.receiver:
                self.user = self.voucher.receiver
            if self.amount != self.voucher.amount:
                self.amount = self.voucher.amount
            if len(self.voucher.donation_set.all()) > 1:
                raise Exception("Can't have more then one donation connected to a Voucher.")
            if self.voucher.status not in [VoucherStatuses.paid, VoucherStatuses.cashed_by_proxy, VoucherStatuses.cashed]:
                raise Exception("Voucher has the wrong status.")
            # TODO: Move logic of changing voucher status to Voucher.
            self.voucher.status = VoucherStatuses.cashed
            self.voucher.save()
            self.status = DonationStatuses.paid


        # Set the datetime when the Donation became 'ready'. This is used for the donation time on the frontend.
        if not self.ready and self.status in (DonationStatuses.pending, DonationStatuses.paid):
            self.ready = timezone.now()
        elif self.ready and self.status not in (DonationStatuses.pending, DonationStatuses.paid):
            self.ready = None

        super(Donation, self).save(*args, **kwargs)


class OrderStatuses(DjangoChoices):
    current = ChoiceItem('current', label=_("Current"))  # The single donation 'shopping cart' (editable).
    recurring = ChoiceItem('recurring', label=_("Recurring"))  # The recurring donation 'shopping cart' (editable).
    closed = ChoiceItem('closed', label=_("Closed"))     # Order with a paid, cancelled or failed payment (not editable).


class Order(models.Model):
    """
    An order is a collection of Donations and vouchers with a connected payment.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"), related_name='old_orders', blank=True, null=True)
    status = models.CharField(_("Status"), max_length=20, choices=OrderStatuses.choices, default=OrderStatuses.current, db_index=True)
    recurring = models.BooleanField(default=False)
    order_number = models.CharField(_("Order Number"), max_length=30, db_index=True, unique=True, help_text="Used to reference the Order from external systems.")

    created = CreationDateTimeField(_("Created"))
    updated = ModificationDateTimeField(_("Updated"))
    # The timestamp the order changed to closed. This is auto-set in the save() method.
    closed = models.DateTimeField(_("Closed"), blank=True, editable=False, null=True)

    @property
    def latest_payment(self):
        """
        Note: this might not always be the related succesful payment.

        Potential fail case: user starts payment with one method, then creates
        another before finishing. Does not finish second one but payment for
        first one succeeds. Now this method still returns the value of the latest
        initiated method.
        """

        if self.payments.count() > 0:
            return self.payments.order_by('-created').all()[0]
        return None

    @property
    def first_donation(self):
        if self.donations.count() > 0:
            return self.donations.all()[0]
        return None


    @property
    def total(self):
        """ Calculated total for this Order. """
        total = 0
        for voucher in self.vouchers.all():
            total += voucher.amount
        for donation in self.donations.all():
            total += donation.amount
        return total

    def __unicode__(self):
        description = ''
        if self.order_number:
            description += self.order_number + " - "

        description += "1%Club "

        donations = self.donations.count()
        vouchers = self.vouchers.count()
        if self.recurring:
            # TODO Use English / Dutch based on user primary_language.
            description += "MAANDELIJKSE DONATIE"
        elif donations == 0 and vouchers > 0:
            if vouchers > 1:
                description += _("GIFTCARDS")
            else:
                description += _("GIFTCARD")
            description += str(self.id)
        elif donations > 0 and vouchers == 0:
            if donations > 1:
                description += _("DONATIONS")
            else:
                description += _("DONATION")
        else:
            description += _("DONATIONS & GIFTCARDS")
        description += " - " + _("THANK YOU!")
        return description

    class Meta:
        ordering = ('-updated',)

    def save(self, *args, **kwargs):
        # http://stackoverflow.com/questions/2076838
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

        # Set the datetime when the Order became 'closed'. This is used for sorting the Order in the admin.
        if not self.closed and self.status == OrderStatuses.closed:
            self.closed = timezone.now()
        elif self.closed and self.status != OrderStatuses.closed:
            self.closed = None

        super(Order, self).save(*args, **kwargs)


    ### METADATA is rather specific here, fetching the metadata of either the fundraiser or the project itself
    def get_tweet(self, **kwargs):
        request = kwargs.get('request', None)
        lang_code = request.LANGUAGE_CODE if request else 'en'
        twitter_handle = settings.TWITTER_HANDLES.get(lang_code, settings.DEFAULT_TWITTER_HANDLE)

        if self.first_donation:
            if self.first_donation.fundraiser:
                title = self.first_donation.fundraiser.owner.get_full_name()
            else:
                title = self.first_donation.project.get_fb_title()

            tweet = _(u"I've just supported {title} {{URL}} via @{twitter_handle}")
            return tweet.format(title=title, twitter_handle=twitter_handle)
        return _(u"{{URL}} via @{twitter_handle}").format(twitter_handle=twitter_handle)

    def get_share_url(self, **kwargs):
        if self.first_donation:
            request = kwargs.get('request')
            # FIXME: Make these urls smarter. At least take language code from current user.
            if self.first_donation.fundraiser:
                fundraiser = self.first_donation.fundraiser
                location = '/en/#!/fundraisers/{0}'.format(fundraiser.id)
            else:
                project = self.first_donation.project
                location = '/en/#!/projects/{0}'.format(project.slug)
            return request.build_absolute_uri(location)
        return None


def link_anonymous_donations(sender, user, request, **kwargs):
    """
    Search for anonymous donations with the same email address as this user and connect them.
    """
    dd_orders = DocDataPaymentOrder.objects.filter(email=user.email).all()

    from bluebottle.wallposts.models import SystemWallPost

    wallposts = None
    for dd_order in dd_orders:
        dd_order.customer_id = user.id
        dd_order.save()
        dd_order.order.user = user
        dd_order.order.save()
        dd_order.order.donations.update(user=user)

        ctype = ContentType.objects.get_for_model(Donation)
        for donation_id in dd_order.order.donations.values_list('id', flat=True):
            qs = SystemWallPost.objects.filter(related_type=ctype, related_id=donation_id)

            if not wallposts:
                wallposts = qs
            else:
                pass
                # This causes errors...
                # wallposts += qs

    if wallposts:
        wallposts.update(author=user)

# On account activation try to connect anonymous donations to this  fails.
user_activated.connect(link_anonymous_donations)

from signals import *
from fundmail import *