from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from django_countries import CountryField

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

    user = models.ForeignKey('auth.User', verbose_name=_("user"), null=True, blank=True)
    amount = MoneyField(_("amount"))
    project = models.ForeignKey('projects.Project', verbose_name=_("project"))

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

    # Store information about the customer here. Mainly useful for anonymous users.
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)
    country = CountryField(default='NL', blank=True, null=True)

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
