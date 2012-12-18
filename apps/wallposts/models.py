from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_extensions.utils.text import truncate_letters
from polymorphic import PolymorphicModel


# This base class will never be used directly because  the content of the wall posts is always defined in the child
# classes. Normally this would be an abstract class but it's not possible to make this an abstract class and have the
# polymorphic behaviour of sorting on the common fields.
class WallPost(PolymorphicModel):
    # The user who wrote the wall post. This can be empty to support wall posts without users (e.g. anonymous text wall
    # posts, system wall posts)
    author = models.ForeignKey('auth.User', blank=True, null=True)

    # The metadata for the wall post.
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ('created',)


class MediaWallPost(WallPost):
    # The content of the wall post.
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=300, blank=True)
    video_url = models.URLField(max_length=100, blank=True)

    def __unicode__(self):
        text = ""
        if self.text:
            text = ": " + truncate_letters(self.text, 50)
        return "MediaWallPost" + text


class TextWallPost(WallPost):
    # The content of the wall post.
    text = models.TextField(max_length=300)

    def __unicode__(self):
        return "TextWallPost: " + truncate_letters(self.text, 50)
