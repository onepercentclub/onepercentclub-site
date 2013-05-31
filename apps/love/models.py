from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField
from apps.love.fields import LoveDeclarationRelation
from apps.love.managers import LoveDeclarationManager


class LoveDeclaration(models.Model):
    """
    A "like" or "favorite" marker expressed by the user for a given object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    creation_date = CreationDateTimeField(_('creation date'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False)

    objects = LoveDeclarationManager()

    class Meta:
        verbose_name = _('Love')
        verbose_name_plural = _('Loves')
        unique_together = ('user', 'content_type', 'object_id')

    def __unicode__(self):
        object_repr = unicode(self.content_object)
        return u"{0} loves {1}".format(self.user, object_repr)


class LovableModel(models.Model):
    """
    Base class for a model which can receive love.
    It adds convenience methods to the model.
    """
    class Meta:
        abstract = True

    #: The received loves for a specific model.
    loves = LoveDeclarationRelation()


    def mark_as_loved(self, user):
        """
        Mark the model as loved by a user.
        """
        # Let the LoveDeclarationManager create the connection.
        LoveDeclaration.objects.mark_as_loved(self, user)


    def unmark_as_loved(self, user):
        """
        Unmark the model as loved by a user.
        """
        # Let the LoveDeclarationManager remove the connection.
        LoveDeclaration.objects.unmark_as_loved(self, user)


    mark_as_loved.alters_data = True
    unmark_as_loved.alters_data = True
