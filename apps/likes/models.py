from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField
from .managers import LikeManager


class Like(models.Model):
    """
    A "like" or "favorite" marker expressed by the user for a given object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    creation_date = CreationDateTimeField(_('creation date'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)

    objects = LikeManager()

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = ('user', 'content_type', 'object_id')

    def __unicode__(self):
        object_repr = unicode(self.content_object)
        return u"{0} likes {1}".format(self.user, object_repr)

