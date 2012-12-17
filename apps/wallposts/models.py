from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django_extensions.utils.text import truncate_letters
from polymorphic import PolymorphicModel


class WallPost(PolymorphicModel):
    # The metadata for the wall post.
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class MediaWallPost(WallPost):
    # The user who wrote the wall post.
    author = models.ForeignKey('auth.User')

    # The content of the wall post
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=300, blank=True)
    video_url = models.URLField(max_length=100, blank=True)

    def __unicode__(self):
        text = ""
        if self.text:
            text = ": " + truncate_letters(self.text, 50)
        return self.__class__.__name__ + text


class TextWallPost(WallPost):
    # The user who wrote the wall post - can be empty to support anonymous text wallposts.
    author = models.ForeignKey('auth.User', blank=True, null=True)

    # The content of the wall post
    text = models.TextField(max_length=300)

    def __unicode__(self):
        return self.__class__.__name__ + ": " + truncate_letters(self.text, 50)
