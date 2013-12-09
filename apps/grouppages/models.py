from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django.conf import settings
from django.db import models
from django.db.models.fields.files import ImageField
from django.utils.translation import ugettext_lazy as _


class GroupPage(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("owner"), help_text=_("Group owner"), related_name="group_owner")

    title = models.CharField(_("title"), max_length=255, unique=True)
    slug = models.SlugField(_("slug"), max_length=100, unique=True)

    created = CreationDateTimeField(_("created"), help_text=_("When this group was created."))
    updated = ModificationDateTimeField(_("updated"))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)

    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    projects = models.ManyToManyField('projects.Project')

    def __unicode__(self):
        return self.title


class GroupPageSlide(models.Model):
    """
    Slides for GroupPage
    """
    group = models.ForeignKey('grouppages.GroupPage')

    tab_text = models.CharField(_("Tab text"), max_length=100, help_text=_("This is shown on tabs beneath the banner."))

    # Contents
    title = models.CharField(_("Title"), max_length=100, blank=True)
    body = models.TextField(_("Body text"), blank=True)
    image = ImageField(_("Image"), max_length=255, blank=True, null=True, upload_to='banner_slides/')
    video_url = models.URLField(_("Video url"), max_length=100, blank=True, default='')

    link_text = models.CharField(_("Link text"), max_length=400, help_text=_("This is the text on the button inside the banner."), blank=True)
    link_url = models.CharField(_("Link url"), max_length=400, help_text=_("This is the link for the button inside the banner."), blank=True)
    style = models.CharField(_("Style"), max_length=40, help_text=_("Styling class name"), default='default', blank=True)

    # Metadata
    sequence = models.IntegerField()
    created = CreationDateTimeField(_('creation date'))
    updated = ModificationDateTimeField(_('last modification'))

    def __unicode__(self):
        return self.group.title + ' :: ' + self.title

    class Meta:
        ordering = ('group', 'sequence')