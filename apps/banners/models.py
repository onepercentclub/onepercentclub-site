from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from django.utils.timezone import now
from django.db.models import Q


class SlideManager(models.Manager):

    def published(self):
        qs = self.get_query_set()
        qs = qs.filter(status=Slide.SlideStatus.published)
        qs = qs.filter(publication_date__lte=now)
        qs = qs.filter(Q(publication_end_date__gte=now) | Q(publication_end_date__isnull=True))
        return qs


class Slide(models.Model):
    """
    Slides for homepage
    """
    class SlideStatus(DjangoChoices):
        published = ChoiceItem('published', label=_("Published"))
        draft = ChoiceItem('draft', label=_("Draft"))

    slug = models.SlugField(_("Slug"))
    language = models.CharField(_("language"), max_length=5, choices=settings.LANGUAGES)
    tab_text = models.CharField(_("Tab text"), max_length=100, help_text=_("This is shown on tabs beneath the banner."))

    # Contents
    title = models.CharField(_("Title"), max_length=100, blank=True)
    body = models.TextField(_("Body text"), blank=True)
    image = ImageField(_("Image"), max_length=255, blank=True, null=True, upload_to='banner_slides/')
    background_image = ImageField(_("Background image"), max_length=255, blank=True, null=True, upload_to='banner_slides/')
    video_url = models.URLField(_("Video url"), max_length=100, blank=True, default='')

    link_text = models.CharField(_("Link text"), max_length=400, help_text=_("This is the text on the button inside the banner."), blank=True)
    link_url = models.CharField(_("Link url"), max_length=400, help_text=_("This is the link for the button inside the banner."), blank=True)
    style = models.CharField(_("Style"), max_length=40, help_text=_("Styling class name"), default='default', blank=True)


    # Publication
    status = models.CharField(_('status'), max_length=20, choices=SlideStatus.choices, default=SlideStatus.draft, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    sequence = models.IntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), editable=False)
    creation_date = CreationDateTimeField(_('creation date'))
    modification_date = ModificationDateTimeField(_('last modification'))

    objects = SlideManager()

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('language', 'sequence')