from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

from djchoices import DjangoChoices, ChoiceItem

from apps.bluebottle_utils.fields import MoneyField


class Donation(models.Model):
    """
    Donation of an amount from a user to a project
    """

    class DonationStatuses(DjangoChoices):
        """
        These statuses are based on the legacy models and need to be updated
        when we actually sort out payments / donations properly, modelled
        after the actual use cases (ie. payout operations, project and
        member notifications). (TODO)
        """
        closed = ChoiceItem('closed', label=_("Closed"))
        expired = ChoiceItem('expired', label=_("Expired"))
        paid = ChoiceItem('paid', label=_("Paid"))
        canceled = ChoiceItem('canceled', label=_("Canceled"))
        chargedback = ChoiceItem('chargedback', label=_("Chargedback"))
        new = ChoiceItem('new', label=_("New"))
        started = ChoiceItem('started', label=_("Started"))


    class DonationTypes(DjangoChoices):
        """
        Different types of donation.
        """
        single = ChoiceItem('single', label=_("Single"))
        recurring = ChoiceItem('recurring', label=_("Recurring"))

    user = models.ForeignKey('auth.User', verbose_name=_("user"), null=True, blank=True)
    amount = MoneyField(_("amount"))
    project = models.ForeignKey('projects.Project', verbose_name=_("project"))

    type = models.CharField(_("type"), max_length=20, choices=DonationTypes.choices, db_index=True,
                            default=DonationTypes.single)

    # Note: having an index here allows for efficient filtering by status.
    status = models.CharField(_("status"), max_length=20, choices=DonationStatuses.choices, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    class Meta:
        verbose_name = _("donation")
        verbose_name_plural = _("donations")

    def __unicode__(self):
        return str(self.id) + ' : ' + self.project.title + ' : EUR ' + str(self.amount)

    def delete(self, using=None):
        # Tidy up! Delete related OrderItem, if any
        OrderItem.objects.filter(object_id=self.id,content_type=ContentType.objects.get_for_model(Donation)).delete()
        return super(Donation, self).delete()


class Order(models.Model):
    """
    Order holds OrderItems (Donations/Vouchers).
    It can be in progress (eg a shopping cart) or processed and paid
    """

    class OrderStatuses(DjangoChoices):
        started = ChoiceItem('started', label=_("Started"))
        checkout = ChoiceItem('checkout', label=_("Checkout"))
        new = ChoiceItem('new', label=_("New"))
        pending = ChoiceItem('pending', label=_("Pending"))
        failed = ChoiceItem('failed', label=_("Failed"))
        paid = ChoiceItem('paid', label=_("Paid"))

    user = models.ForeignKey('auth.User', verbose_name=_("user"), null=True)

    status = models.CharField(_("status"),max_length=20, choices=OrderStatuses.choices, db_index=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    payment = models.ForeignKey('cowry.Payment', null=True)

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
    order  = models.ForeignKey(Order)
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


class RecurringDonation(models.Model):
    """
    Settings for a recurring donation,
    The actual donations will be generated monthly by a celery/cron job.
    """

    user = models.ForeignKey('auth.User')
    amount = MoneyField()

    # TODO: We probably want to store this encrypted
    billing_number = models.CharField(max_length=12)
    billing_name = models.CharField(max_length=100)
    billing_city = models.CharField(max_length=200)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))

    projects = models.ManyToManyField('projects.Project')

