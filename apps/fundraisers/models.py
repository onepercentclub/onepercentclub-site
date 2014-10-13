from bluebottle.utils.utils import StatusDefinition
from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum
from django.utils.http import urlquote
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from sorl.thumbnail import ImageField

#from apps.fund.models import DonationStatuses


class FundRaiser(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("initiator"), help_text=_("Project owner"))
    project = models.ForeignKey(settings.PROJECTS_PROJECT_MODEL, verbose_name=_("project"))

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    image = ImageField(_("picture"), max_length=255, blank=True, null=True, upload_to='fundraiser_images/', help_text=_("Minimal of 800px wide"))
    video_url = models.URLField(max_length=100, blank=True, default='')

    amount = models.PositiveIntegerField(_("amount (in cents)"))
    currency = models.CharField(max_length="10", default='EUR')
    deadline = models.DateTimeField(null=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this fundraiser was created."))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)

    def __unicode__(self):
        return self.title

    @property
    def amount_donated(self):
        # FIXME: Removed import of DonationStatuses because it was resulting in circular imports.
        valid_statuses = [StatusDefinition.PENDING, StatusDefinition.PAID]
        donations = self.donation_set.filter(order__status__in=valid_statuses)
        if donations:
            total = donations.aggregate(sum=Sum('amount'))
            return total['sum']
        return '000'

    def get_meta_title(self, **kwargs):
        return self.title

    get_fb_title = get_meta_title # alias for metadata in apps/fund/models.py:Order

    def get_tweet(self, **kwargs):
        # NOTE: mention user in hashtag or something like that?
        request = kwargs.get('request', None)
        lang_code = request.LANGUAGE_CODE if request else 'en'
        twitter_handle = settings.TWITTER_HANDLES.get(lang_code, settings.DEFAULT_TWITTER_HANDLE)

        title = urlquote(self.get_meta_title(**kwargs))

        # {URL} is replaced in Ember to fill in the page url, avoiding the
        # need to provide front-end urls in our Django code.
        tweet = _(u"{title} {{URL}} via @{twitter_handle}").format(
                    title=title, twitter_handle=twitter_handle
                )

        return tweet


from fundwallmails import *