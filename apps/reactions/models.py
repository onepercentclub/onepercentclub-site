from apps.bluebottle_utils.managers import GenericForeignKeyManagerMixin
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField


REACTION_MAX_LENGTH = getattr(settings, 'REACTION_MAX_LENGTH', 500)


class ReactionWithDeletedManager(GenericForeignKeyManagerMixin, models.Manager):
    pass


class ReactionManager(GenericForeignKeyManagerMixin, models.Manager):

    def get_query_set(self):
        query_set = super(ReactionManager, self).get_query_set()
        query_set = query_set.order_by('created')
        return query_set.filter(deleted__isnull=True)


class Reaction(models.Model):
    """
    A user reaction about some object. This model is based on the Comments model
    from django.contrib.comments.
    """

    # Who posted this reaction. User will need to be logged in to make a reaction.
    author = models.ForeignKey('auth.User', verbose_name=_('author'), related_name="%(class)s_reaction")
    editor = models.ForeignKey('auth.User', verbose_name=_('editor'), blank=True, null=True, help_text=_("The last user to edit this reaction."))

    # The reaction text.
    text = models.TextField(_('reaction text'), max_length=REACTION_MAX_LENGTH)

    # Metadata for the reaction.
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Manager
    objects = ReactionManager()
    objects_with_deleted = ReactionWithDeletedManager()

    class Meta:
        ordering = ('created',)
        verbose_name = _('reaction')
        verbose_name_plural = _('reactions')

    def __unicode__(self):
        s = "{0}: {1}".format(self.author.get_full_name(), self.text)
        return Truncator(s).words(10)
