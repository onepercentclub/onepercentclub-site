from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from polymorphic import PolymorphicModel


class WallPost(PolymorphicModel):
    # The user who wrote the wall post.
    author = models.ForeignKey('auth.User')

    # The metadata for the wall post.
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class MediaWallPost(WallPost):
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=300, blank=True)
    video_url = models.URLField(max_length=100, blank=True)

    def __unicode__(self):
        text = ""
        if self.text and len(self.text) > 50:
            text = ": " + self.text[:50]
        elif self.text:
            text = ": " + self.text
        return self.__class__.__name__ + text


class TextWallPost(WallPost):
    text = models.TextField(max_length=300)

    def __unicode__(self):
        if len(self.text) > 50:
            text = self.text[:50]
        else:
            text = self.text
        return self.__class__.__name__ + ": " + text