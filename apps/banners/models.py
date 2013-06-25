from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from fluent_contents.models import PlaceholderField


class Slide(models.Model):
    """
    Slides for homepage
    """
    class SlideStatus(DjangoChoices):
        published = ChoiceItem('published', label=_("Published"))
        draft = ChoiceItem('draft', label=_("Draft"))

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"))

    # Contents
    language = models.CharField(_("language"), max_length=5, choices=settings.LANGUAGES)
    contents = PlaceholderField("blog_contents")

    # Publication
    status = models.CharField(_('status'), max_length=20, choices=SlideStatus.choices, default=SlideStatus.draft, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    sequence = models.IntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), editable=False)
    creation_date = CreationDateTimeField(_('creation date'))
    modification_date = ModificationDateTimeField(_('last modification'))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('language', 'sequence')