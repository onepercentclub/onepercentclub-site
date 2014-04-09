from bluebottle.bb_organizations.models import BaseOrganization, BaseOrganizationMember, BaseOrganizationDocument
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from djchoices import DjangoChoices, ChoiceItem


from bluebottle.utils.models import Address
from django.core.files.storage import FileSystemStorage


class Organization(BaseOrganization):
    """
    Organizations can run Projects. An organization has one or more members.
    """
    registration = models.FileField(upload_to='organizations/registrations', storage=FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT), null=True, blank=True)

    account_bank_name = models.CharField(_("account bank name"), max_length=255, blank=True)
    account_bank_address = models.CharField(_("account bank address"), max_length=255, blank=True)
    account_bank_country = models.ForeignKey('geo.Country', blank=True, null=True, related_name="account_bank_country")
    account_iban = IBANField(_("account IBAN"), blank=True)
    account_bic = SWIFTBICField(_("account SWIFT-BIC"), blank=True)
    account_number = models.CharField(_("account number"), max_length=255, blank=True)
    account_name = models.CharField(_("account name"), max_length=255, blank=True)
    account_city = models.CharField(_("account city"), max_length=255, blank=True)
    account_other = models.CharField(_("account information that doesn't fit in the other field"), max_length=255, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def full_clean(self, exclude=None):
        if not self.slug:
            original_slug = slugify(self.name)
            slug = original_slug
            next = 2
            while not slug or Organization.objects.filter(slug=slug):
                slug = '%s%s%s' % (original_slug, '-', next)
                next += 1
            self.slug = slug


class OrganizationMember(BaseOrganizationMember):
    pass


class OrganizationDocument(BaseOrganizationDocument):
    pass
