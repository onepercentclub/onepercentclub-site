from apps.bluebottle_utils.managers import GenericForeignKeyManagerMixin
from apps.reactions.models import Reaction
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from polymorphic import PolymorphicModel, PolymorphicManager


class WallPostManager(GenericForeignKeyManagerMixin, PolymorphicManager):
    pass


# This base class will never be used directly because  the content of the wall posts is always defined in the child
# classes. Normally this would be an abstract class but it's not possible to make this an abstract class and have the
# polymorphic behaviour of sorting on the common fields.
class WallPost(PolymorphicModel):
    # The user who wrote the wall post. This can be empty to support wall posts without users (e.g. anonymous text wall
    # posts, system wall posts)
    author = models.ForeignKey('auth.User', verbose_name=_('author'), related_name="%(class)s_wallpost", blank=True, null=True)
    editor = models.ForeignKey('auth.User', verbose_name=_('editor'), blank=True, null=True, help_text=_("The last user to edit this wallpost."))

    # The metadata for the wall post.
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Manager
    objects = WallPostManager()

    @property
    # TODO: See if we can make a manager out of this or hav another need solution
    # Define reactions so it will always use WallPost ContentType
    # Using generic.GenericRelation(Reaction) the ContentType will be overwritten by the subclasses (eg MediaWallPost)
    def reactions(self):
        content_type = ContentType.objects.get_for_model(WallPost)
        return Reaction.objects.filter(object_id=self.id, content_type=content_type)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return str(self.id)


class MediaWallPost(WallPost):
    # The content of the wall post.
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=300, blank=True, default='')
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
    text = models.TextField(max_length=300)

    def __unicode__(self):
        return Truncator(self.text).words(10)
