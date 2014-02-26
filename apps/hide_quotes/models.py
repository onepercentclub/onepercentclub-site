from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from django.utils.timezone import now
from django.db.models import Q


class QuoteManager(models.Manager):

    def published(self):
        qs = self.get_query_set()
        qs = qs.filter(status=Quote.QuoteStatus.published)
        qs = qs.filter(publication_date__lte=now)
        qs = qs.filter(Q(publication_end_date__gte=now) | Q(publication_end_date__isnull=True))
        return qs


class Quote(models.Model):
    """
    Slides for homepage
    """
    class QuoteStatus(DjangoChoices):
        published = ChoiceItem('published', label=_("Published"))
        draft = ChoiceItem('draft', label=_("Draft"))

    class QuoteSegment(DjangoChoices):
        projects = ChoiceItem('projects', label=_("Projects"))
        tasks = ChoiceItem('tasks', label=_("Tasks"))
        befriend = ChoiceItem('befriend', label=_("Befriend"))

    # Contents
    language = models.CharField(_("language"), max_length=5, choices=settings.LANGUAGES)
    quote = models.TextField()
    segment = models.CharField(_("type"), max_length=20, choices=QuoteSegment.choices, db_index=True)

    # Publication
    status = models.CharField(_('status'), max_length=20, choices=QuoteStatus.choices, default=QuoteStatus.draft, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_("When the entry should go live, status must be 'Published'."))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Author'), related_name="quote_author", editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Quoted member'), related_name="quote_user")

    creation_date = CreationDateTimeField(_('creation date'))
    modification_date = ModificationDateTimeField(_('last modification'))

    objects = QuoteManager()

    def __unicode__(self):
        return self.quote

