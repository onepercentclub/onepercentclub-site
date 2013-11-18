from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from sorl.thumbnail import ImageField


class FundRaiser(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("initiator"), help_text=_("Project owner"))
    project = models.ForeignKey('projects.Project', verbose_name=_("project"))

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    image = ImageField(_("picture"), max_length=255, blank=True, null=True, upload_to='fundraiser_images/', help_text=_("Minimal of 800px wide"))
    video_url = models.URLField(max_length=100, blank=True, default='')

    amount = models.PositiveIntegerField(_("amount (in cents)"))
    deadline = models.DateTimeField(null=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this fundraiser was created."))
    updated = ModificationDateTimeField(_('updated'))

    def __unicode__(self):
        return self.title