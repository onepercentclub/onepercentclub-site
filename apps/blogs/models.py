from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import comments
from django.contrib.contenttypes.generic import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from fluent_contents.models import PlaceholderField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from sorl.thumbnail import ImageField
from apps.geo.models import Country
from .managers import BlogPostManager


class BlogCategory(models.Model):
    title = models.CharField(_("Title"), max_length=200)

    class Meta:
        verbose_name = _("Blog category")
        verbose_name_plural = _("Blog categories")

    def __unicode__(self):
        return self.title


# Based on https://github.com/edoburu/django-fluent-blogs/
# which doesn't offer custom base class models yet.
class BlogPost(models.Model):
    """
    Blog post / news item.
    """
    class PostStatus(DjangoChoices):
        published = ChoiceItem('published', label=_("Published"))
        draft = ChoiceItem('draft', label=_("Draft"))

    class PostType(DjangoChoices):
        blog = ChoiceItem('blog', label=_("Blog"))
        news = ChoiceItem('news', label=_("News"))

    post_type = models.CharField(_("Type"), max_length=20, choices=PostType.choices)
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"))

    # Contents
    main_image = ImageField(_("Main photo"), upload_to='blogs', blank=True)
    language = models.CharField(_("language"), max_length=5, unique=True, choices=settings.LANGUAGES)
    contents = PlaceholderField("blog_contents")

    # Publication
    status = models.CharField(_('status'), max_length=20, choices=PostStatus.choices, default=PostStatus.draft, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)
    allow_comments = models.BooleanField(_("Allow comments"), default=True)

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Taxonomy
    categories = models.ManyToManyField(BlogCategory, verbose_name=_("Categories"), blank=True)
    tags = TaggableManager(blank=True)
    countries = models.ManyToManyField(Country, verbose_name=_("Countries"), blank=True, null=True)

    objects = BlogPostManager()
    all_comments = GenericRelation(comments.get_model(), verbose_name=_("Comments"), object_id_field='object_pk')


    @property
    def comments(self):
        """
        Return the visible comments.
        """
        return comments.get_model().objects.for_model(self).filter(is_public=True)


    @property
    def previous_entry(self):
        """
        Return the previous entry
        """
        entries = self.__class__.objects.published().filter(publication_date__lt=self.publication_date).order_by('-publication_date')[:1]
        return entries[0] if entries else None


    @property
    def next_entry(self):
        """
        Return the next entry
        """
        entries = self.__class__.objects.published().filter(publication_date__gt=self.publication_date).order_by('publication_date')[:1]
        return entries[0] if entries else None
