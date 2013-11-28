from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_iban.fields import IBANField, SWIFTBICField
from djchoices import DjangoChoices, ChoiceItem
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager

from bluebottle.bluebottle_utils.models import Address
from django.core.files.storage import FileSystemStorage


class Organization(models.Model):
    """
    Organizations can run Projects. An organization has one or more members.
    """
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    description = models.TextField(_("description"), blank=True)
    legal_status = models.TextField(_("legal status"), blank=True, help_text=_("The legal status of the organization (e.g. Foundation)."))
    phone_number = models.CharField(_("phone number"), max_length=40, blank=True)
    website = models.URLField(_("website"), blank=True)

    email = models.EmailField(blank=True)
    twitter = models.CharField(_("twitter"), max_length=255, blank=True)
    facebook = models.CharField(_("facebook"), max_length=255, blank=True)
    skype = models.CharField(_("skype"), max_length=255, blank=True)

    legal_status = models.CharField(max_length=255, blank=True)
    registration = models.FileField(upload_to='organizations/registrations', storage=FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT), null=True, blank=True)

    created = CreationDateTimeField(_("created"))
    updated = ModificationDateTimeField(_("updated"))
    deleted = models.DateTimeField(_("deleted"), null=True, blank=True)

    partner_organizations = models.TextField(_("partner organizations"), blank=True)

    account_bank_name = models.CharField(_("account bank name"), max_length=255, blank=True)
    account_bank_address = models.CharField(_("account bank address"), max_length=255, blank=True)
    account_bank_country = models.ForeignKey('geo.Country', blank=True, null=True, related_name="account_bank_country")
    account_iban = IBANField(_("account IBAN"), blank=True)
    account_bic = SWIFTBICField(_("account SWIFT-BIC"), blank=True)
    account_number = models.CharField(_("account number"), max_length=255, blank=True)
    account_name = models.CharField(_("account name"), max_length=255, blank=True)
    account_city = models.CharField(_("account city"), max_length=255, blank=True)
    account_other = models.CharField(_("account information that doesn't fit in the other field"), max_length=255, blank=True)

    # Address
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.ForeignKey('geo.Country', blank=True, null=True, related_name="country")
    postal_code = models.CharField(max_length=20, blank=True)

    tags = TaggableManager(blank=True, verbose_name=_("tags"))

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


class OrganizationMember(models.Model):
    """ Members from a Organization """

    class MemberFunctions(DjangoChoices):
        owner = ChoiceItem('owner', label=_("Owner"))
        editor = ChoiceItem('editor', label=_("Editor"))

    organization = models.ForeignKey(Organization, verbose_name=_("organization"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))
    function = models.CharField(_("function"), max_length=20, choices=MemberFunctions.choices)

    class Meta:
        verbose_name = _("organization member")
        verbose_name_plural = _("organization members")


class OrganizationDocument(models.Model):
    """ Document for an Organization """

    organization = models.ForeignKey(Organization, verbose_name=_("organization"))
    file = models.FileField(upload_to='organizations/documents', storage=FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), blank=True, null=True)

    @property
    def document_url(self):
        content_type = ContentType.objects.get_for_model(OrganizationDocument).id
        return reverse('document-download-detail', kwargs={'content_type': content_type, 'pk': self.pk})

    class Meta:
        verbose_name = _("organization document")
        verbose_name_plural = _("organization documents")

