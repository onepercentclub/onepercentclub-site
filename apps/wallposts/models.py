from apps.bluebottle_utils.managers import GenericForeignKeyManagerMixin
from apps.reactions.models import Reaction, ReactionManager
from django.contrib.comments import get_model
from django.db import models
from django.db.models import get_model
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from polymorphic import PolymorphicModel, PolymorphicManager


import os
import random
import string
import mimetypes
#import magic

import logging
logger = logging.getLogger(__name__)

def generate_filename(instance, filename):
    """
    Creates a random directory and file name for uploaded pictures.

    The random directory allows the uploaded images to be evenly spread over
    1296 x 1296 directories. This allows us to host more files before hitting bad
    performance of the OS filesystem and/or utility programs which can occur
    when a directory has thousands of files.

    An example return value is of this method is:
        'profiles/tw/s9/tws9ea4eqaj37xnu24svp2vwndsytzysa.jpg'
    """

    # Create the upload directory string.
    char_set = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(char_set) for i in range(33))
    directory_prefix = instance.__class__.__name__.lower()
    upload_directory = os.path.join(directory_prefix, random_string[0:2], random_string[2:4])

    # Get the file extension from the original filename. At this point the image
    # is verified when using the Django ImageFile form.
    # TODO Make this general for all files. Right now it's specific to Action.picture.
    mime_type = instance.picture.file.content_type

    if mime_type == 'image/jpeg':
        # mimetype.guess_extension() returns '.jpe' for jpegs but that's not frequently used.
        file_extension = '.jpg'
    else:
        file_extension = mimetypes.guess_extension(mime_type)

    # mimetype.guess_extension() can return None so deal with this case.
    if not file_extension:
        original_filename = os.path.basename(filename)
        file_extension = os.path.splitext(original_filename)[1]
        logger.warning("Can't detect file extension for %s. Using guessed extension \'%s\'" %
                       (original_filename, file_extension))

    # Create the normalized path.
    normalized_filename = random_string + file_extension
    return os.path.normpath(os.path.join(upload_directory, normalized_filename))




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
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)

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

    def save(self, *args, **kwargs):
        # We overwrite save to enable 'empty' IP
        if self.ip_address == "":
            self.ip_address = None
        super(WallPost, self).save(*args, **kwargs)

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
