from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from djchoices import DjangoChoices, ChoiceItem
from fluent_contents.models import PlaceholderField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from sorl.thumbnail import ImageField
from bluebottle.geo.models import Country
from .managers import BlogPostManager, BlogPostProxyManager


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

    post_type = models.CharField(_("Type"), max_length=20, choices=PostType.choices, db_index=True)
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"))

    # Contents
    main_image = ImageField(_("Main photo"), upload_to='blogs', blank=True)
    language = models.CharField(_("language"), max_length=5, choices=settings.LANGUAGES)
    contents = PlaceholderField("blog_contents")

    # Publication
    status = models.CharField(_('status'), max_length=20, choices=PostStatus.choices, default=PostStatus.draft, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)
    allow_comments = models.BooleanField(_("Allow comments"), default=True)

    # Metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), editable=False)
    creation_date = CreationDateTimeField(_('creation date'))
    modification_date = ModificationDateTimeField(_('last modification'))

    # Taxonomy
    categories = models.ManyToManyField(BlogCategory, verbose_name=_("Categories"), blank=True)
    tags = TaggableManager(blank=True)
    countries = models.ManyToManyField(Country, verbose_name=_("Countries"), blank=True, null=True)

    objects = BlogPostManager()

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        unique_together = ('slug', 'language',)
        ordering = ('-publication_date', )

    def __unicode__(self):
        return self.title


# The proxy models are only here to have a separation in the Django admin interface.

class BlogPostProxy(BlogPost):
    """
    A subset of the ``BlogPost`` model that only displays real blog posts.
    """
    limit_to_post_type = BlogPost.PostType.blog
    objects = BlogPostProxyManager()

    class Meta:
        proxy = True
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")

    def save(self, *args, **kwargs):
        self.post_type = self.limit_to_post_type
        super(BlogPostProxy, self).save(*args, **kwargs)


class NewsPostProxy(BlogPost):
    """
    A subset of the ``BlogPost`` model that only displays news items.
    """
    limit_to_post_type = BlogPost.PostType.news
    objects = BlogPostProxyManager()

    class Meta:
        proxy = True
        verbose_name = _("News")
        verbose_name_plural = _("News")

    def save(self, *args, **kwargs):
        self.post_type = self.limit_to_post_type
        super(NewsPostProxy, self).save(*args, **kwargs)
