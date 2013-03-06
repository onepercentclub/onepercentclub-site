from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django.conf import settings
from polymorphic import PolymorphicModel
from .managers import ReactionManager, WallPostManager


WALLPOST_TEXT_MAX_LENGTH = getattr(settings, 'WALLPOST_TEXT_MAX_LENGTH', 300)
WALLPOST_REACTION_MAX_LENGTH = getattr(settings, 'WALLPOST_REACTION_MAX_LENGTH', 300)


class WallPost(PolymorphicModel):
    """
    The WallPost base class. This class will never be used directly because the content of a WallPost is always defined
    in the child classes.

    Implementation Note: Normally this would be an abstract class but it's not possible to make this an abstract class
    and have the polymorphic behaviour of sorting on the common fields.
    """

    # The user who wrote the wall post. This can be empty to support wall posts without users (e.g. anonymous
    # TextWallPosts, system WallPosts for donations etc.)
    author = models.ForeignKey('auth.User', verbose_name=_('author'), related_name="%(class)s_wallpost", blank=True, null=True)
    editor = models.ForeignKey('auth.User', verbose_name=_('editor'), blank=True, null=True, help_text=_("The last user to edit this wallpost."))

    # The metadata for the wall post.
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Manager
    objects = WallPostManager()

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return str(self.id)


class MediaWallPost(WallPost):
    # The content of the wall post.
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH, blank=True, default='')
    video_url = models.URLField(max_length=100, blank=True, default='')
    # This is temporary and will go away when we figure out how to upload related photos.
    photo = models.ImageField(upload_to='mediawallpostphotos', blank=True, null=True)

    def __unicode__(self):
        return Truncator(self.text).words(10)


class MediaWallPostPhoto(models.Model):
    mediawallpost = models.ForeignKey(MediaWallPost, related_name='photos')
    photo = models.ImageField(upload_to='mediawallpostphotos')


class TextWallPost(WallPost):
    # The content of the wall post.
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH)

    def __unicode__(self):
        return Truncator(self.text).words(10)


class Reaction(models.Model):
    """
    A user reaction or comment to a WallPost. This model is based on the Comments model from django.contrib.comments.
    """

    # Who posted this reaction. User will need to be logged in to make a reaction.
    author = models.ForeignKey('auth.User', verbose_name=_('author'), related_name='wallpost_reactions')
    editor = models.ForeignKey('auth.User', verbose_name=_('editor'), blank=True, null=True, related_name='+', help_text=_("The last user to edit this reaction."))

    # The reaction text and the wallpost it's a reaction to.
    text = models.TextField(_('reaction text'), max_length=WALLPOST_REACTION_MAX_LENGTH)
    wallpost = models.ForeignKey(WallPost, related_name='reactions')

    # Metadata for the reaction.
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Manager
    objects = ReactionManager()
    objects_with_deleted = models.Manager()

    class Meta:
        ordering = ('created',)
        verbose_name = _('Reaction')
        verbose_name_plural = _('Reactions')

    def __unicode__(self):
        s = "{0}: {1}".format(self.author.get_full_name(), self.text)
        return Truncator(s).words(10)
